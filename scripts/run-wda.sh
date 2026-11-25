#!/bin/bash
# 起 WebDriverAgent（它会一直占着这个终端窗口，关掉窗口手指就没了）。值同 build-wda.sh。
UDID="你的旧 iPhone 的 UDID"
TEAM="你的 Apple 开发者 Team ID"
BUNDLE="com.example.WebDriverAgentRunner"
WDA_DIR="$HOME/WebDriverAgent"
cd "$WDA_DIR" && xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner \
  -destination "id=$UDID" -derivedDataPath ../wda-dd \
  DEVELOPMENT_TEAM="$TEAM" PRODUCT_BUNDLE_IDENTIFIER="$BUNDLE" test-without-building
