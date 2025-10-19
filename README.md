# Fastest Video Splitter

A lightweight, portable Windows application for splitting video files into equal segments without re-encoding. Built with Python and Tkinter, featuring embedded FFmpeg for zero dependencies.

## Features

- 🚀 **Lightning Fast**: Uses FFmpeg's stream copy mode (no re-encoding)
- 📁 **Portable**: Single executable, no installation required
- 🎯 **Simple Interface**: User-friendly GUI for easy operation
- ⚡ **No Quality Loss**: Direct stream copying preserves original quality
- 🔧 **Customizable**: Adjustable segment duration
- 📊 **Progress Tracking**: Real-time progress updates
- 🗂️ **Smart Naming**: Automatic output file naming

## Download

Get the latest release from the [Releases page](https://github.com/mehmetgozlemeci/FastestVideoSplitter/releases).

## Usage

1. **Select Source Video**: Click "Browse" to choose your input video file
2. **Choose Output Directory**: Select where to save the split segments
3. **Set Segment Duration**: Enter desired segment length in minutes (default: 20)
4. **Split Video**: Click "Split Video" to start the process
5. **Get Results**: Find your split files in the output directory

### Output File Naming

Input: `MyVideo.mp4`  
Output: 
- `MyVideo_splitted_001.mp4`
- `MyVideo_splitted_002.mp4` 
- `MyVideo_splitted_003.mp4`
- ...

## Supported Formats

- MP4, AVI, MKV, MOV, WMV, FLV, WebM, and more!

## How It Works

The application uses FFmpeg's `segment` muxer with stream copying:
```bash
ffmpeg -i input.mp4 -c copy -segment_time 00:20:00 -f segment output_%03d.mp4
