{ pkgs ? (import <nixpkgs> {}).pkgs }:
with pkgs;
mkShell {
  buildInputs = [
    python310Packages.virtualenv 
    python310Packages.pip 
  ];
  shellHook = ''
    # fixes libstdc++ issues and libgl.so issues
    LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib/:/run/opengl-driver/lib/
    source ./env.sh
  '';
}
