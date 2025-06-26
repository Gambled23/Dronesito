{ }:

let
  # 1) Define an overlay that really touches pkgs.opencv4
  myOverlay = final: prev: {
    opencv4 = prev.opencv4.overrideAttrs (oldAttrs: rec {
      # flip on the CUDA bits that the stock recipe left off
      enableCuda   = true;
      enableCudnn  = true;
      enableCublas = true;
      enableCufft  = true;

      # pull in the toolkit & libs the CMakeLists will look for
      buildInputs = oldAttrs.buildInputs ++ [
        final.cudaPackages.cudatoolkit
        final.cudaPackages.cudnn
        final.cudaPackages.libcublas
        final.cudaPackages.libcufft
        final.libGLU
        final.libGL
        final.xorg.libX11
        final.xorg.libXi
        final.xorg.libXmu
      ];

      # extend exactly the same `cmakeFlags` you saw in the log
      cmakeFlags = oldAttrs.cmakeFlags ++ [
        "-DCMAKE_POLICY_DEFAULT_CMP0146=NEW"
        "-DCUDA_TOOLKIT_ROOT_DIR=${final.cudaPackages.cudatoolkit}"
        "-DCUDA_ARCH_BIN=8.6"
        "-DWITH_CUDA=ON"
        "-WITH_NVCUVID=ON"
        "-DWITH_CUDNN=ON"
        "-DOPENCV_DNN_CUDA=ON"
        "-DCUDA_FAST_MATH=ON"
        "-DWITH_CUBLAS=ON"
        "-DWITH_CUFFT=ON"
        "-DBUILD_opencv_cudacodec=ON"
        "-DOPENCV_ENABLE_NONFREE=ON"
        "-DCUDA_NVCC_FLAGS=--expt-relaxed-constexpr"
        "-DCMAKE_VERBOSE_MAKEFILE=ON"
      ];

      # ensure the build really sees your CUDA env
      preConfigure = (oldAttrs.preConfigure or "") + ''
        export CUDA_PATH=${final.cudaPackages.cudatoolkit}
        export CUDA_HOME=${final.cudaPackages.cudatoolkit}
        export CUDNN_HOME=${final.cudaPackages.cudnn}
        export NVCCFLAGS="-gencode arch=compute_86,code=sm_86"
      '';
    });
  };

  # 2) Import nixpkgs *with* that overlay
  pkgs = import <nixpkgs> {
    config.allowUnfree = true;
    overlays = [ myOverlay ];
  };

  # 3) Your Python env (now pulling in the new CUDA-built opencv4)
  pythonEnv = pkgs.python312.withPackages (ps: with ps; [
    numpy mysql-connector setuptools flask flask-cors pymongo deepface yt-dlp wheel dlib
    opencv4
  ]);
in

# 4) Use mkShell for a dev shell
pkgs.mkShell {
  name = "cvCuda_test";

  buildInputs = [
    pkgs.cudaPackages.cudatoolkit
    pkgs.linuxPackages.nvidia_x11
    pkgs.opencv4      # <— this is now your CUDA-enabled OpenCV!
    pythonEnv         # and your Python with cv2 bound to that build
  ];

  shellHook = ''
    export PATH=${pythonEnv}/bin:$PATH
    echo "🔮 Welcome to Quartzite Dev Shell!"
    echo "CUDA Opencv4 → $(python3 -c 'import cv2; print(cv2.getBuildInformation().splitlines()[0])')"
    python3 - <<<'import cv2; print("CUDA devices:", cv2.cuda.getCudaEnabledDeviceCount())'
  '';
}