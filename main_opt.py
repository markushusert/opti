#!/usr/bin/python3
import manage_optimierung
import settings
import os
import sys

settings.g_calculationfolder_rel="populations"


def main():
    manage_optimierung.create_empty_generation("dummy_generation")

if __name__=="__main__":
    main()