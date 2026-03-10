{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    python311
    python311Packages.numpy
    python311Packages.pandas
    python311Packages.matplotlib
    python311Packages.reportlab
    python311Packages.pyaml
  ];
}