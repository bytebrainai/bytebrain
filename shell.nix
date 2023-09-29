{ pkgs ? (import <nixpkgs> {}).pkgs }:
with pkgs;
mkShell {
  buildInputs = [
    python310
    python310Packages.ipython
    python310Packages.virtualenv
    python310Packages.pip
    stdenv.cc.cc.lib
    gcc-unwrapped.lib
    docker-compose
    nodejs
    yarn
    zlib
    guake
    fish
    vim
    git
  ];

  shellHook = ''
    LD_LIBRARY_PATH="${lib.makeLibraryPath [stdenv.cc.cc.lib zlib ] }"
    export $(cat .env | xargs)
  '';
}
