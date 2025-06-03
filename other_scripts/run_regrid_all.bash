
#!/bin/bash
module load nco
export griddir=/glade/u/home/timand/remapping/

hor_res=mpasa60
out_res=0.5x0.5

hor_res=mpasa120
out_res=1x1

exptype=cntrl
#exptype=T298
#exptype=U0X2
#exptype=GAP1

srcgrid=${hor_res}
dstgrid=${out_res}

expname=sy_dcmip2025_horiz_mount_flow_${hor_res}_${exptype}
input_dir="/glade/work/simchany/dcmip25/${expname}/run"

# Loop through each relevant file in the directory
for filepath in ${input_dir}/${expname}.cam.h0i.*.nc; do
  # Extract the date part from the filename
  filename=$(basename "$filepath") # Get just the filename, not the full path
  datename=$(echo "$filename" | sed -n 's/.*\.h0i\.\(.*\)\.nc/\1/p')

  echo ${filename}
  filename_no_ext="${filepath%.nc}"
  cd ${input_dir}

  ncremap -m ${griddir}map_${srcgrid}_to_${dstgrid}_aave.nc ${filename} ${filename_no_ext}.regrid.${out_res}.nc

done
