# [天草应援纪念馆](http://www.sky-grass.com)

[![MIT license](https://img.shields.io/badge/license-MIT-blue.svg?maxAge=2592000)](COPYING)

An archive of SNH48-王晓佳应援会's Weibo content, before its catastrophic destruction on Sep 1, 2017. The account has since been reincarnated, so to speak, but lost content could not be reclaimed on Weibo, hence this site.

Disclaimer: I'm not affiliated with the group in any way. Someone reached out and asked for a favor, and I was just happy to help out.

Another disclaimer: I'm not a web dev. This repo has its fair share of hacks, the stitched-together build system will make a pro web dev roll their eyes, and many things are probably far away from best practice. I know.

## Prerequisites

- Python 3.6 or later;
- yarn v1.0.0 or later;
- GNU make;
- Zsh;
- ImageMagick, if you want to generate an entirely local site; not necessary if you use sinaimg.cn as image source.

bower is needed to update assets in `bower_components`, but since the assets are already checked in, bower is not a build time dependency.

## Build instructions

```sh
make prereqs
make site
# To build an entirely local copy
make site-local
```

The static site is generated in `public`. You may explore the configuration files in `configs` for available config options.

## Credit

Lost data was recovered by [@你的档案](http://weibo.com/hecaitou001) of [微博看看](http://weibo.wbdacdn.com/e) fame.

Credit also goes to other parties listed on [the site's About page](http://sky-grass.com/about).

## License

Code is released under the MIT license. All rights reserved on textual and imagery content.
