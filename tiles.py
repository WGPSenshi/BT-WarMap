import gdal2tiles, subprocess

gdal2tiles.generate_tiles('C:/Users/Senshi/git/roguetechmap/public/galaxy.png', 'C:/Users/Senshi/git/roguetechmap/public/tiles', profile = "raster", np_processes=8)