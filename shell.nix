{ pkgs ? (import <nixpkgs> {}).pkgs }:
with pkgs;
mkShell {
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
    source ./env.sh
  '';
}
