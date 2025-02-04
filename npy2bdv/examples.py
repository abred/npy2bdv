import time
import sys
import numpy as np
import npy2bdv


def generate_test_image(dim_yx):
    """Gaussian blob spanning the whole range of uint16 type"""
    x = np.linspace(-3, 3, dim_yx[1])
    y = np.linspace(-3, 3, dim_yx[0])
    x, y = np.meshgrid(x, y)
    return 65535 * np.exp(- ((x ** 2) / 2 + (y ** 2) / 2))


# Basic writing
print("Example1: writing 2 time points and 2 channels\n")
plane = generate_test_image((1024, 2048))
stack = []
for z in range(50):
    stack.append(plane)
stack = np.asarray(stack)

fname = "./ex1_t2_ch2.h5"
bdv_writer = npy2bdv.BdvWriter(fname, nchannels=2, subsamp=((1, 1, 1),))
bdv_writer.append_view(stack, time=0, channel=0)
bdv_writer.append_view(stack, time=0, channel=1)
bdv_writer.append_view(stack, time=1, channel=0)
bdv_writer.append_view(stack, time=1, channel=1)
bdv_writer.write_xml_file(ntimes=2)
bdv_writer.close()
print("Synthetic data is written into " + fname + "\n")

# Writing speed test
print("Example2: speed test for 20 time points and 2 channels. File size is 7 GB!\n")
ntimes = 20
nchannels = 2
start_time_total = time.time()
i_stacks = 0
time_list = []

fname = "./ex2_t20_chan2.h5"
bdv_writer = npy2bdv.BdvWriter(fname, nchannels=2, subsamp=((1, 1, 1),))
for ichannel in range(nchannels):
    for itime in range(ntimes):
        start_time = time.time()
        bdv_writer.append_view(stack, time=itime, channel=ichannel)
        time_interval = time.time() - start_time
        time_list.append(time_interval)
        i_stacks += 1.0

bdv_writer.write_xml_file(ntimes=ntimes)
bdv_writer.close()
time_per_stack = (time.time() - start_time_total) / i_stacks
print("H5 mean writing time per stack: {:1.3f}".format(time_per_stack) + " sec.")
print("H5 mean writing speed: " + str(int(sys.getsizeof(stack) / time_per_stack / 1e6)) + " MB/s")
print("Synthetic data is written into " + fname + "\n")

# Writing with affine transformations defined in XML file
print("Example3: writing 1 time point and 1 channel with 10-px un-shear transformation along X axis.\n" +
      "With non-isotropic voxel size calibration.")
shear_x_px = 10
affine_matrix = np.array(((1.0, 0.0, -shear_x_px, 0.0),
                          (0.0, 1.0, 0.0, 0.0),
                          (0.0, 0.0, 1.0, 0.0)))

fname = "./ex3_t1_ch1_unshear.h5"
bdv_writer = npy2bdv.BdvWriter(fname, nchannels=1, subsamp=((1, 1, 1),))
bdv_writer.append_view(stack, time=0, channel=0,
                       m_affine=affine_matrix,
                       name_affine="unshearing transformation",
                       calibration=(1, 1, 1))
bdv_writer.write_xml_file(ntimes=1)
bdv_writer.close()
print("(Un)sheared stack is written into " + fname + "\n")

# Writing with experiment metadata
print("Example4: writing 1 time point and 1 channel with voxel size, exposure, camera and microscope properties\n")
fname = "./ex4_t1_ch1_cam_props.h5"
bdv_writer = npy2bdv.BdvWriter(fname, nchannels=1, subsamp=((1, 1, 1),))
bdv_writer.append_view(stack, time=0, channel=0,
                       voxel_size_xyz=(1, 1, 5), voxel_units='um',
                       exposure_time=10, exposure_units='ms')
bdv_writer.write_xml_file(ntimes=1, camera_name="Hamamatsu OrcaFlash100",
                          microscope_name='Superscope',
                          user_name='nvladimus')
bdv_writer.close()
print("Stack is written into " + fname + "\n")

# Writing with subsampling and compression
print("Example5: 1 time point and 1 channel with 3-level subsampling and compression")
fname = "./ex5_t1_ch1_level3_gzip.h5"
bdv_writer = npy2bdv.BdvWriter(fname, nchannels=1,
                               subsamp=((1, 1, 1), (2, 4, 4), (4, 16, 16)),
                               blockdim=((64, 64, 64),),
                               compression='gzip')
bdv_writer.append_view(stack, time=0, channel=0)
bdv_writer.write_xml_file(ntimes=1)
bdv_writer.close()
print("Stack with subsampling is written into " + fname + "\n")

# Writing virtual stacks that are too big to fit RAM
print("Example6: 1 time point, 1 channel, huge virtual stack, 40 GB!\n")
stack_dim_zyx = (1000, 3648, 5472)
image_plane = generate_test_image(stack_dim_zyx[1:])

fname = "./ex6_t1_ch1_huge_virtual.h5"
bdv_writer = npy2bdv.BdvWriter(fname, nchannels=1,
                               blockdim=((1, int(image_plane.shape[0]/4), int(image_plane.shape[1]/4)),))
bdv_writer.append_view(stack=None, virtual_stack_dim=stack_dim_zyx, time=0, channel=0)
for i in range(stack_dim_zyx[0]):
    bdv_writer.append_plane(plane=image_plane, plane_index=i, time=0, channel=0)

bdv_writer.write_xml_file(ntimes=1)
bdv_writer.close()
print("Virtual stack is is written into " + fname + "\n")