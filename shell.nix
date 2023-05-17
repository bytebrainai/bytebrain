{ pkgs ? (import <nixpkgs> {}).pkgs }:
with pkgs;
mkShell {
  LD_LIBRARY_PATH = "${stdenv.cc.cc.lib}/lib";
  buildInputs = [
    python310Packages.virtualenv 
    python310Packages.pip 
    docker-compose
    stdenv.cc.cc.lib
    pam
    fish
    nodejs
    yarn
  ];
  shellHook = ''
    # fixes libstdc++ issues and libgl.so issues
    LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib/:/run/opengl-driver/lib/
    source ./env.sh
  '';
}
