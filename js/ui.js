/* global $, Cookies, Mousetrap */

/*! momo.zhimingwang.org | ui.js v1 | MIT/Expat */

$(function () {
  var $window = $(window)
  var $document = $(document)
  var $body = $('body')
  var $nav = $('nav')
  var $audioControl = $('#audio-control')

  // https://github.com/Modernizr/Modernizr/blob/master/feature-detects/touchevents.js
  var hasTouchSupport = ('ontouchstart' in window) ||
      (window.DocumentTouch && document instanceof window.DocumentTouch)

  var isHome = window.location.pathname.match(/\/(index(\.html)?)?$/)
  var isPaginated = window.location.pathname.match(/\/\d+(\.html)?$/)

  if (window.baiduTrackerId) {
    var trackingScriptUrl = `https://hm.baidu.com/hm.js?${window.baiduTrackerId}`
    delete window.baiduTrackerId
    $.ajaxSetup({ cache: true })  // hm.baidu.com/hm.js does not work with a timestamp paramter
    $.getScript(trackingScriptUrl)
  }

  $.fn.extend({
    onScreen: function () {
      if (this.length === 0) {
        return false
      }
      var viewportTop = $window.scrollTop()
      var viewportBottom = viewportTop + $window.height()
      var top = this.offset().top
      var bottom = top + this.height()
      return (top >= viewportTop && top < viewportBottom) ||
        (bottom > viewportTop && bottom <= viewportBottom) ||
        (top <= viewportTop && bottom >= viewportBottom)
    },
    scrollTo: function () {
      if (this.length > 0) {
        $window.scrollTop(this.offset().top - 30)
      }
      return this
    },
    prevStatus: function () {
      return this.prevAll('.status').first()
    },
    nextStatus: function () {
      return this.nextAll('.status').first()
    },
    highlight: function () {
      if (this.length > 0) {
        // Dehighlight other highlighted elements first
        $('.highlight').removeClass('highlight')
        this.first().addClass('highlight')
      }
      return this
    },
    dehighlight: function () {
      this.removeClass('highlight')
      return this
    }
  })

  var isMobileLayout = function () {
    return $window.width() < 880
  }

  var topVisibleStatus = function () {
    var viewportTop = $window.scrollTop()
    var viewportBottom = viewportTop + $window.height()
    return $('.status').filter(function () {
      var top = this.offsetTop
      var bottom = top + this.offsetHeight
      return (top >= viewportTop && top < viewportBottom) ||
        (top <= viewportTop && bottom >= viewportBottom)
    }).first()
  }

  var bottomVisibleStatus = function () {
    var viewportTop = $window.scrollTop()
    var viewportBottom = viewportTop + $window.height()
    return $('.status').filter(function () {
      var top = this.offsetTop
      var bottom = top + this.offsetHeight
      return (bottom > viewportTop && bottom <= viewportBottom) ||
        (top <= viewportTop && bottom >= viewportBottom)
    }).last()
  }

  // iOS Safari hack to work around the click-handler-not-firing bug
  // http://stackoverflow.com/a/16006333
  if (/iPad|iPhone|iPod/.test(window.navigator.userAgent)) {
    $('body').css('cursor', 'pointer')
  }

  // Lazyload, if applicable
  $('img.lazy').lazyload({
    threshold: 800,
    // Smallest possible transparent PNG file
    // https://kidsreturn.org/2011/04/smallest-possible-1x1-transparent-gif-and-png/
    // http://garethrees.org/2007/11/14/pngcrush/
    placeholder: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=='
  })

  // Scroll to last recorded position (except on /)
  if (!isHome) {
    $window.scrollTop(Cookies.get('scroll'))
  }

  // Dropdown menu
  $('.menu-toggle').click(function () {
    $('.menu').slideToggle(300)
  })
  $document.click(function (e) {
    // Hide the dropdown menu when anything other than the toggle is clicked
    if (isMobileLayout() && !$(e.target).hasClass('menu-toggle')) {
      $('.menu').slideUp(300)
    }
  })
  $window.resize(function () {
    if (isMobileLayout()) {
      $('.menu').hide()
    } else {
      $nav.show()
      $('.menu').show()
    }
  })

  // Hide/show nav on scroll
  // Credit: https://jsfiddle.net/mariusc23/s6mLJ/31/
  ;(function () {
    var lastScrollTop = 0
    $window.scroll($.throttle(100, function () {
      if (isMobileLayout()) {
        var scrollTop = $window.scrollTop()
        // Scrolled more than 20 pixels
        if (Math.abs(lastScrollTop - scrollTop) > 20) {
          if (scrollTop > lastScrollTop && scrollTop > $nav.height()) {
            // Scrolling down (past the top nav bar)
            $nav.slideUp(100)
            $audioControl.slideUp(100)
          } else {
            // Scrolling up
            if (scrollTop + $window.height() < $document.height()) {
              // Exclude the case of bouncing at the bottom of page
              $nav.slideDown(100)
              $audioControl.slideDown(100)
            }
          }
          lastScrollTop = scrollTop
        }
      }
    }))
  })()

  // Extend jQuery with fancybox and status initializer
  $.fn.extend({
    initFancybox: function () {
      this.fancybox({
        // Eliminate animations in desktop browsers (note that setting speed to 0 would break things)
        speed: hasTouchSupport ? 300 : 1,
        thumbs: true,
        slideShow: {
          speed: 1500
        },
        buttons : [
          'open',
          'slideShow',
          'fullScreen',
          'thumbs',
          'close'
        ],
        btnTpl : {
          open: '<button data-fancybox-open class="fancybox-button fancybox-button--open" title="打开原图(O)"></button>',
          slideShow: '<button data-fancybox-play class="fancybox-button fancybox-button--play" title="幻灯片(P)"></button>',
          fullScreen: '<button data-fancybox-fullscreen class="fancybox-button fancybox-button--fullscreen" title="全屏(F)"></button>',
          thumbs: '<button data-fancybox-thumbs class="fancybox-button fancybox-button--thumbs" title="缩略图(G)"></button>',
          close: '<button data-fancybox-close class="fancybox-button fancybox-button--close" title="关闭(Esc)"></button>'
        },
        onInit: function (instance) {
          Mousetrap.pause()

          var $openButton = instance.$refs.toolbar.find('[data-fancybox-open]')
          $openButton.click(function () { window.open($(this).attr('data-src')) })

          $document.on('keypress.inside-fancybox', function (e) {
            var key = String.fromCharCode(e.which)
            switch (key) {
              case 'a':
              case ',':
              case '<':
                // Previous
                instance.previous(1)
                break

              case 'd':
              case '.':
              case '>':
                // Next
                instance.next(1)
                break

              case 'o':
              case 'q':
                // Close
                instance.close()
                break

              case 'O':
                // Open original image
                $openButton.click()
                break

              default:
                return true
            }
            return false
          })
        },
        beforeShow: function (instance, current) {
          instance.$refs.toolbar.find('[data-fancybox-open]').attr('data-src', current.src)
        },
        beforeClose: function () {
          $document.off('keypress.inside-fancybox')
        },
        afterClose: function () {
          Mousetrap.unpause()
        }
      })

      // Gif overlay
      this.filter('[href$=".gif"]').append($('<div class="gif-indicator">GIF</div>'))

      return this
    },

    initStatus: function () {
      this.each(function (i, e) {
        var $status = $(e)
        if (!$status.hasClass('status')) {
          console.error('Not a status:', e)
        }

        // Add data-fancybox and data-status-url to fancybox images, and initialize fancybox
        var statusId = $status.attr('id')
        $status.find('.fancybox').attr('data-fancybox', statusId).initFancybox()

        // Click to highlight
        $status.click(function () {
          $(this).highlight()
        })
      })

      return this
    }
  })

  $('.status').initStatus()

  // Register click actions
  $('.back-to-top').click(function () {
    $window.scrollTop(0)
  })

  $document.click(function (e) {
    var clickedTag = e.target.tagName.toLowerCase()
    if (clickedTag === 'html' || clickedTag === 'body') {
      $('.status.highlight').dehighlight()
    }
  })

  // Page specific
  if (isHome) {
    ;(function () {
      const totalPages = window.totalPages
      if (!totalPages > 0) {
        throw new Error('window.totalPages not found.')
      }
      delete window.totalPages
      const totalStatuses = window.totalStatuses
      if (!totalStatuses > 0) {
        throw new Error('window.totalStatuses not found.')
      }
      delete window.totalStatuses
      var page = 1
      var statusCount = 0

      var loadNextPage = function (options, successCallback, failureCallback) {
        if (page > totalPages || statusCount >= totalStatuses) {
          console.error('All statuses have been loaded.')
          return
        }

        options = options || {}
        var changeHash = options.changeHash || false
        var scrollToTop = options.scrollToTop || false
        var scrollToBottom = options.scrollToBottom || false
        var animate = options.animate || false

        var $anchor = $('main hr').last()
        $anchor.attr('id', page)
        $('.loading').remove()
        $('<div class="loading">加载中</div>').insertAfter($anchor)

        $.get(`/${page}/`, function (html) {
          var $dummy = $('<div>').html(html)
          $dummy.find('main .status').first().prevAll().remove()
          $dummy.find('main hr').last().nextAll().remove()
          $dummy.find('.status').initStatus()

          // Do not change hash to #1 on the initial page
          if (changeHash && page !== 1) {
            window.location.hash = `#${page}`
          }

          $('.loading').remove()

          $dummy.find('main > *').insertAfter($anchor)
          $dummy.remove()

          statusCount = $('.status').length
          $('.info-nav-bar .left').text(`已加载${statusCount}/${totalStatuses}条状态`)

          if (scrollToTop || scrollToBottom) {
            var position
            if (scrollToTop) {
              position = $anchor.offset().top - 32
            } else {
              position = $document.height()
            }
            if (animate) {
              $body.animate({scrollTop: position}, 300)
            } else {
              $window.scrollTop(position)
            }
          }

          page += 1

          if (page > totalPages || statusCount >= totalStatuses) {
            $window.off('scroll.loadnext')
          }

          typeof successCallback === 'function' && successCallback()
        }).fail(function () {
          // AJAX failure
          console.error(`Failed to fetch /${page}/`)
          $('.loading').addClass('fail').text('加载失败')

          typeof failureCallback === 'function' && failureCallback()
        })
      }

      var loadPages = function (count, successCallback, failureCallback) {
        if (page + count > totalPages) {
          console.error(`Cannot load ${count} pages; only ${totalPages - page} pages remain.`)
          return
        }

        var recurse = function (remaining) {
          if (remaining > 0) {
            loadNextPage({scrollToBottom: true}, recurse.bind(null, remaining - 1), failureCallback)
          } else if (remaining === 0) {
            typeof successCallback === 'function' && successCallback()
          }
        }
        recurse(count)
      }

      var registerLoadNextHandler = function () {
        $window.on('scroll.loadnext', $.throttle(100, function () {
          var scrollTop = $window.scrollTop()
          if (scrollTop + $window.height() >= $document.height() - 500) {
            // Skip if currently loading
            if ($('.loading:not(.fail)').length === 0) {
              loadNextPage({changeHash: true}, function () {
                // Restore previous scroll position to prevent jumping around
                $window.scrollTop(scrollTop)
              })
            }
          }
        }))
      }

      ;(function () {
        var m = window.location.hash.match(/^#([1-9][0-9]*)$/)
        if (m && parseInt(m[1]) <= totalPages) {
          loadPages(
            parseInt(m[1]) - 1,
            function () {
              loadNextPage({scrollToTop: true}, registerLoadNextHandler, registerLoadNextHandler)
            },
            registerLoadNextHandler
          )
        } else {
          window.location.hash = ''
          loadNextPage({changeHash: true}, registerLoadNextHandler, registerLoadNextHandler)
        }
      })()
    })()
  }

  if (isPaginated) {
    // Add page switcher
    const totalPages = window.totalPages
    if (!totalPages > 0) {
      throw new Error('window.totalPages not found.')
    }
    delete window.totalPages
    const currentPage = window.currentPage
    if (!currentPage > 0) {
      throw new Error('window.currentPage not found.')
    }
    delete window.currentPage
    var innerHtml = `<form>
第 <input type="text" name="page" pattern="\\d+" value=${currentPage} title="仅限页码"> /${totalPages}页
<input type="submit" hidden>
</form>`
    $('.info-nav-bar .left').html(innerHtml)
    $('.info-nav-bar .left form').submit(function (e) {
      var targetPage = parseInt($(this).find('input[name=page]').val())
      if (targetPage >= 1 && targetPage <= totalPages) {
        window.location.href = targetPage.toString()
      }
      e.preventDefault()
    })
  }

  // Keyboard shortcuts
  // Unregister g *
  for (var ch = 97; ch <= 122; ch++) {
    Mousetrap.bind('g ' + String.fromCharCode(ch), null)
  }
  // g h => /
  Mousetrap.bind('g h', function () {
    window.location = '/'
  })
  // g A => /all
  Mousetrap.bind('g A', function () {
    window.location = '/all'
  })
  // G, b => bottom
  Mousetrap.bind(['G', 'b'], function () {
    $window.scrollTop($document.height())
    return false
  })
  // g g, t => top
  Mousetrap.bind(['g g', 't'], function () {
    $window.scrollTop(0)
    return false
  })
  // a, ',', <, left => previous page
  Mousetrap.bind(['a', ',', '<', 'left'], function () {
    var prev = $('.prev a').get(0)
    if (prev) {
      prev.click()
    }
    return false
  })
  // d, '.', >, right => next page
  Mousetrap.bind(['d', '.', '>', 'right'], function () {
    var next = $('.next a').get(0)
    if (next) {
      next.click()
    }
    return false
  })
  // j, k / s, w => highlight and navigate
  Mousetrap.bind(['s', 'j'], function () {
    var $highlighted = $('.status.highlight')
    if ($highlighted.length === 0) {
      topVisibleStatus().highlight().scrollTo()
    } else {
      $highlighted.nextStatus().highlight().scrollTo()
    }
    return false
  })
  Mousetrap.bind(['w', 'k'], function () {
    var $highlighted = $('.status.highlight')
    if ($highlighted.length === 0) {
      bottomVisibleStatus().highlight().scrollTo()
    } else {
      $highlighted.prevStatus().highlight().scrollTo()
    }
    return false
  })
  // o => open image
  Mousetrap.bind('o', function () {
    var $highlighted = $('.status.highlight')
    // Open image in currently highlighted status if the status is currently on screen
    if ($highlighted.length > 0 && $highlighted.onScreen()) {
      $highlighted.find('.gallery a').first().click()
      return false
    }
    // Open the first at least 3/4 visible image (and highlight the corresponding status)
    var viewportTop = $window.scrollTop()
    var viewportBottom = viewportTop + $window.height()
    var img = $('.gallery a').filter(function () {
      var top = this.offsetTop
      var bottom = top + this.offsetHeight
      return top >= viewportTop - 30 && bottom <= viewportBottom + 30
    }).first()
    if (img.length === 0) {
      return false
    }
    img.closest('.status').highlight()
    img.click()
    return false
  })

  // Record scroll position upon unload
  $window.on('beforeunload', function () {
    Cookies.set('scroll', $window.scrollTop(), {path: window.location.pathname})
  })

  // Audio playback
  var audio = $('#audio').get(0)
  // Set audio volume to 40% in order not to startle people
  audio.volume = 0.4
  $audioControl.click(function () {
    var $this = $(this)
    if ($this.hasClass('playing')) {
      audio.pause()
    } else {
      audio.play()
    }
    $this.toggleClass('playing')
  })
})
