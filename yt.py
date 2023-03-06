import concurrent.futures
import time
import os
import moviepy
import moviepy.editor
from pytube import YouTube
from pytube import Playlist
from tqdm import tqdm
from pytube import Stream
import argparse


def downloadVideo(url,path,resolution="max"):
  try:
      def progress_callback(stream: Stream, data_chunk: bytes, bytes_remaining: int) -> None:
        pbar.update(len(data_chunk))
      
      # Create a YouTube object and get the highest resolution stream    
      yt = YouTube(url)
      yt.register_on_progress_callback(progress_callback)
      streams = yt.streams
      # Filter streams based on type and resolution
      if resolution == "max":
        stream = streams.filter(progressive=False, type="video", file_extension="webm")
        stream = stream.order_by("resolution").desc().first()
      else:
          stream = streams.filter(progressive=False, type="video", file_extension="webm", resolution=resolution)
          stream = stream.desc().first()
          
      current_resolution = stream.resolution

      # Select the stream with the highest video and audio bitrate
      audio_stream = streams.filter(progressive=False, type="audio", file_extension="mp4")
      audio_stream = audio_stream.order_by("abr").desc().first()
      
      video_stream_name = f"{stream.default_filename[:-5]}-{current_resolution}.webm"
      audio_stream_name = f"{audio_stream.default_filename[:-4]}-{current_resolution}.mp4"    
      
      video_list_folder = [files for files in os.listdir(path)]
      if audio_stream_name in video_list_folder:
          print("Already Avaiable:",audio_stream_name)
          return
      print("Download Started:",audio_stream_name)
      print()
      pbar = tqdm(total=stream.filesize, unit="bytes")
      print()
      stream.download(output_path=path, filename=video_stream_name, max_retries=2)
      pbar.close()


      audio_stream.download(output_path=path, filename=audio_stream_name, max_retries=2)
      
      
      # Merge audio and video into single mp4 file
      moviepy.video.io.ffmpeg_tools.ffmpeg_merge_video_audio(
        
        os.path.join(path,video_stream_name), #Video File
        os.path.join(path,audio_stream_name), #Audio File
        os.path.join(path,f"Processed {audio_stream_name}") #Output File
        
      )
      
      # Remove temporary audio and video files
      os.remove(os.path.join(path,video_stream_name))
      os.remove(os.path.join(path,audio_stream_name))
      
      # Rename the main file to original name
      os.rename(os.path.join(path,f"Processed {audio_stream_name}"), os.path.join(path,audio_stream_name))
     
      print("Downloaded:",audio_stream_name)
      print()

  except Exception as e:
    print(e)
    try:
     os.remove(os.path.join(path,video_stream_name))
     os.remove(os.path.join(path,audio_stream_name))
    except Exception as E:
      print(E)  


def downloadPlaylist(url,path,resolution="max"):
    try:
        playlist = Playlist(url)
        video_urls = playlist.video_urls
        print("Downloading Playlist:",playlist.title)
        print("Total Videos:",len(video_urls))
        path = [path for _ in range(len(video_urls))]
        resolution = [resolution for _ in range(len(video_urls))]
        with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(downloadVideo, video_urls, path, resolution)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    
    # Get the home directory path for the current user
    home_dir = os.path.expanduser("~")

    # Get the default download folder path for the current user
    if os.name == "nt":  # Windows
        download_dir = os.path.join(home_dir, "Downloads")
    elif os.name == "posix":  # macOS/Linux
        download_dir = os.path.join(home_dir, "Downloads")
    else:
        download_dir = None
      
    parser = argparse.ArgumentParser(description="A CLI utility to download YouTube videos and Whole YouTube Playlist")
    # Create an argument group for the required arguments
    required_args = parser.add_argument_group("Required Arguments")
    # Add command line arguments
    required_args.add_argument("--url", type=str, help="URL of the Video/Playlist to Download", required=True)
    parser.add_argument("--loc", type=str, help="Location to Save Videos", default=download_dir)
    parser.add_argument("--res", type=str, help="Resolution of Video or Whole Playlist", default="max")
    parser.add_argument("--playlist", action="store_true", help="Specify this to Download Playlist")

    # Parse the arguments
    args = parser.parse_args()

    # Use the arguments in your code
    if args.playlist:
        initTime = time.time()
        downloadPlaylist(args.url, args.loc, args.res)
        finalTime = time.time()
        print(f"Processes Completed In: {time.strftime('%H:%M:%S', time.gmtime(finalTime-initTime))}")    
    else:
        initTime = time.time()
        downloadVideo(args.url, args.loc, args.res)
        finalTime = time.time()
        print(f"Process Completed In: {time.strftime('%H:%M:%S', time.gmtime(finalTime-initTime))}")






   
   
