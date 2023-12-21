#===------------------------------------------------------------------------===#
#
# Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
#===------------------------------------------------------------------------===#

# There are currently no unsupported files.
set(UNSUPPORTED_FILES "")

# There are currently no unimplemented files.
set(UNIMPLEMENTED_FILES "")

file(GLOB SKIPPED_FILES CONFIGURE_DEPENDS
  # These files are only intended to be run on AArch64, but we don't currently
  # process the target attribute, so these are disabled everywhere. When the
  # DejaGNU target attribute is handled correctly, these should be removed from
  # here.
  pr100981.f90
  pr100981-1.f90
  pr108979.f90
  pr99656.f90
  pr99721.f90
  pr99807.f90
  pr99825.f90
  pr99924.f90

  # These files are only intended to be run on PowerPC, but we don't currently
  # process the target attribute, so these are disabled everywhere. When the
  # DejaGNU target attribute is handled correctly, these should be removed from
  # here.
  pr45714-b.f
)

# These tests fail when they are expected to pass.
file(GLOB FAILING_FILES CONFIGURE_DEPENDS
  # These tests fail at runtime.
  pr60510.f

  # These tests fail to compile when compilation is expected to succeed.
  pr90681.f
  pr97761.f90
  pr99746.f90
  vect-8.f90
  vect-8-epilogue.F90
)
