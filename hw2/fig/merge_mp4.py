from moviepy.editor import VideoFileClip, clips_array

var='hw2'
flist = ['rce_walker_15k_05m_p3.mp4','rce_walker_15k_1m_p3.mp4','rce_walker_1k_1m_p3.mp4','rce_walker_1k_2m_p3.mp4']

# merge vedio
clip0 = VideoFileClip(var+'.'+flist[0])
clip1 = VideoFileClip(var+'.'+flist[1])
clip2 = VideoFileClip(var+'.'+flist[2])
clip3 = VideoFileClip(var+'.'+flist[3])
final_clip = clips_array([[clip0, clip1], [clip2, clip3]])
outfile = var+'.mp4'
print(outfile)
final_clip.write_videofile(outfile, codec='libx264', ffmpeg_params=['-pix_fmt','yuv420p'],threads=8)
