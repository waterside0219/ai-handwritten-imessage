#!/bin/bash
# 编译 WebDriverAgent 并装到手机上。先填下面四个值。要在 Mac 自带的"终端"App 里跑（见教程第 3 步）。
UDID="你的旧 iPhone 的 UDID"          # xcrun devicectl list devices
TEAM="你的 Apple 开发者 Team ID"
BUNDLE="com.example.WebDriverAgentRunner"   # 换成你自己的反向域名
WDA_DIR="$HOME/WebDriverAgent"        # git clone https://github.com/appium/WebDriverAgent
cd "$WDA_DIR" && xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner \
  -destination "id=$UDID" -derivedDataPath ../wda-dd -allowProvisioningUpdates \
  DEVELOPMENT_TEAM="$TEAM" CODE_SIGN_STYLE=Automatic PRODUCT_BUNDLE_IDENTIFIER="$BUNDLE" build-for-testing
