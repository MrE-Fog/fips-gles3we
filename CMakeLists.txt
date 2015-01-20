cmake_minimum_required(VERSION 2.8)

# include the fips main cmake file
get_filename_component(FIPS_ROOT_DIR "../fips" ABSOLUTE)
include("${FIPS_ROOT_DIR}/cmake/fips.cmake")

include_directories(include)

fips_setup()
fips_project(fips-glesw3)
fips_add_subdirectory(include/GLES3)
fips_finish()

