#!/usr/bin/env bash
cd "$(dirname "$0")"
osascript -e "display notification \"Spotify playlist shuffle started\" with title \"Job launched\""
poetry run python main.py 7BMrXBnMPlEiHb0Nd7QcUR