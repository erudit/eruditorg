!function(e){function t(t){for(var n,o,s=t[0],l=t[1],u=t[2],f=0,d=[];f<s.length;f++)o=s[f],Object.prototype.hasOwnProperty.call(r,o)&&r[o]&&d.push(r[o][0]),r[o]=0;for(n in l)Object.prototype.hasOwnProperty.call(l,n)&&(e[n]=l[n]);for(c&&c(t);d.length;)d.shift()();return a.push.apply(a,u||[]),i()}function i(){for(var e,t=0;t<a.length;t++){for(var i=a[t],n=!0,s=1;s<i.length;s++){var l=i[s];0!==r[l]&&(n=!1)}n&&(a.splice(t--,1),e=o(o.s=i[0]))}return e}var n={},r={21:0},a=[];function o(t){if(n[t])return n[t].exports;var i=n[t]={i:t,l:!1,exports:{}};return e[t].call(i.exports,i,i.exports,o),i.l=!0,i.exports}o.m=e,o.c=n,o.d=function(e,t,i){o.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:i})},o.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},o.t=function(e,t){if(1&t&&(e=o(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var i=Object.create(null);if(o.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var n in e)o.d(i,n,function(t){return e[t]}.bind(null,n));return i},o.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return o.d(t,"a",t),t},o.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},o.p="";var s=window.webpackJsonp=window.webpackJsonp||[],l=s.push.bind(s);s.push=t,s=s.slice();for(var u=0;u<s.length;u++)t(s[u]);var c=l;a.push([140,0]),i()}({140:function(e,t,i){"use strict";i.r(t);i(98),i(332),i(334)},30:function(e,t,i){"use strict";function n(e,t){for(var i=0;i<t.length;i++){var n=t[i];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}i.d(t,"a",(function(){return r}));function r(){$("form#id-login-form").validate({rules:{username:{required:!0},password:{required:!0}},messages:{username:gettext("Ce champ est obligatoire."),password:gettext("Ce champ est obligatoire.")}})}var a=function(){function e(){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.previousURL=null,this.modalSelector="#login-modal, #article-login-modal, #journal-login-modal",this.init()}var t,i,a;return t=e,(i=[{key:"init",value:function(){this.modal()}},{key:"modal",value:function(){var e=this;$(this.modalSelector).magnificPopup({mainClass:"mfp-fade",removalDelay:750,type:"ajax",closeOnBgClick:!1,closeBtnInside:!0,ajax:{settings:{beforeSend:function(e){e.setRequestHeader("X-PJAX","true")}}},callbacks:{beforeOpen:function(){e.previousURL=window.location.pathname},open:function(){history.replaceState(null,null,$($.magnificPopup.instance.currItem.el).attr("href")),$("body").addClass("modal-open")},ajaxContentAdded:function(){r()},close:function(){history.replaceState(null,null,e.previousURL),$("body").removeClass("modal-open")}}})}}])&&n(t.prototype,i),a&&n(t,a),e}();t.b=a},332:function(e,t,i){i(11)(i(333))},333:function(e,t){e.exports='/*! lazysizes - v5.2.2 */\n\n!function(e){var t=function(u,D,f){"use strict";var k,H;if(function(){var e;var t={lazyClass:"lazyload",loadedClass:"lazyloaded",loadingClass:"lazyloading",preloadClass:"lazypreload",errorClass:"lazyerror",autosizesClass:"lazyautosizes",srcAttr:"data-src",srcsetAttr:"data-srcset",sizesAttr:"data-sizes",minSize:40,customMedia:{},init:true,expFactor:1.5,hFac:.8,loadMode:2,loadHidden:true,ricTimeout:0,throttleDelay:125};H=u.lazySizesConfig||u.lazysizesConfig||{};for(e in t){if(!(e in H)){H[e]=t[e]}}}(),!D||!D.getElementsByClassName){return{init:function(){},cfg:H,noSupport:true}}var O=D.documentElement,a=u.HTMLPictureElement,P="addEventListener",$="getAttribute",q=u[P].bind(u),I=u.setTimeout,U=u.requestAnimationFrame||I,l=u.requestIdleCallback,j=/^picture$/i,r=["load","error","lazyincluded","_lazyloaded"],i={},G=Array.prototype.forEach,J=function(e,t){if(!i[t]){i[t]=new RegExp("(\\\\s|^)"+t+"(\\\\s|$)")}return i[t].test(e[$]("class")||"")&&i[t]},K=function(e,t){if(!J(e,t)){e.setAttribute("class",(e[$]("class")||"").trim()+" "+t)}},Q=function(e,t){var i;if(i=J(e,t)){e.setAttribute("class",(e[$]("class")||"").replace(i," "))}},V=function(t,i,e){var a=e?P:"removeEventListener";if(e){V(t,i)}r.forEach(function(e){t[a](e,i)})},X=function(e,t,i,a,r){var n=D.createEvent("Event");if(!i){i={}}i.instance=k;n.initEvent(t,!a,!r);n.detail=i;e.dispatchEvent(n);return n},Y=function(e,t){var i;if(!a&&(i=u.picturefill||H.pf)){if(t&&t.src&&!e[$]("srcset")){e.setAttribute("srcset",t.src)}i({reevaluate:true,elements:[e]})}else if(t&&t.src){e.src=t.src}},Z=function(e,t){return(getComputedStyle(e,null)||{})[t]},s=function(e,t,i){i=i||e.offsetWidth;while(i<H.minSize&&t&&!e._lazysizesWidth){i=t.offsetWidth;t=t.parentNode}return i},ee=function(){var i,a;var t=[];var r=[];var n=t;var s=function(){var e=n;n=t.length?r:t;i=true;a=false;while(e.length){e.shift()()}i=false};var e=function(e,t){if(i&&!t){e.apply(this,arguments)}else{n.push(e);if(!a){a=true;(D.hidden?I:U)(s)}}};e._lsFlush=s;return e}(),te=function(i,e){return e?function(){ee(i)}:function(){var e=this;var t=arguments;ee(function(){i.apply(e,t)})}},ie=function(e){var i;var a=0;var r=H.throttleDelay;var n=H.ricTimeout;var t=function(){i=false;a=f.now();e()};var s=l&&n>49?function(){l(t,{timeout:n});if(n!==H.ricTimeout){n=H.ricTimeout}}:te(function(){I(t)},true);return function(e){var t;if(e=e===true){n=33}if(i){return}i=true;t=r-(f.now()-a);if(t<0){t=0}if(e||t<9){s()}else{I(s,t)}}},ae=function(e){var t,i;var a=99;var r=function(){t=null;e()};var n=function(){var e=f.now()-i;if(e<a){I(n,a-e)}else{(l||r)(r)}};return function(){i=f.now();if(!t){t=I(n,a)}}},e=function(){var v,m,c,h,e;var y,z,g,p,C,b,A;var n=/^img$/i;var d=/^iframe$/i;var E="onscroll"in u&&!/(gle|ing)bot/.test(navigator.userAgent);var _=0;var w=0;var N=0;var M=-1;var x=function(e){N--;if(!e||N<0||!e.target){N=0}};var W=function(e){if(A==null){A=Z(D.body,"visibility")=="hidden"}return A||!(Z(e.parentNode,"visibility")=="hidden"&&Z(e,"visibility")=="hidden")};var S=function(e,t){var i;var a=e;var r=W(e);g-=t;b+=t;p-=t;C+=t;while(r&&(a=a.offsetParent)&&a!=D.body&&a!=O){r=(Z(a,"opacity")||1)>0;if(r&&Z(a,"overflow")!="visible"){i=a.getBoundingClientRect();r=C>i.left&&p<i.right&&b>i.top-1&&g<i.bottom+1}}return r};var t=function(){var e,t,i,a,r,n,s,l,o,u,f,c;var d=k.elements;if((h=H.loadMode)&&N<8&&(e=d.length)){t=0;M++;for(;t<e;t++){if(!d[t]||d[t]._lazyRace){continue}if(!E||k.prematureUnveil&&k.prematureUnveil(d[t])){R(d[t]);continue}if(!(l=d[t][$]("data-expand"))||!(n=l*1)){n=w}if(!u){u=!H.expand||H.expand<1?O.clientHeight>500&&O.clientWidth>500?500:370:H.expand;k._defEx=u;f=u*H.expFactor;c=H.hFac;A=null;if(w<f&&N<1&&M>2&&h>2&&!D.hidden){w=f;M=0}else if(h>1&&M>1&&N<6){w=u}else{w=_}}if(o!==n){y=innerWidth+n*c;z=innerHeight+n;s=n*-1;o=n}i=d[t].getBoundingClientRect();if((b=i.bottom)>=s&&(g=i.top)<=z&&(C=i.right)>=s*c&&(p=i.left)<=y&&(b||C||p||g)&&(H.loadHidden||W(d[t]))&&(m&&N<3&&!l&&(h<3||M<4)||S(d[t],n))){R(d[t]);r=true;if(N>9){break}}else if(!r&&m&&!a&&N<4&&M<4&&h>2&&(v[0]||H.preloadAfterLoad)&&(v[0]||!l&&(b||C||p||g||d[t][$](H.sizesAttr)!="auto"))){a=v[0]||d[t]}}if(a&&!r){R(a)}}};var i=ie(t);var B=function(e){var t=e.target;if(t._lazyCache){delete t._lazyCache;return}x(e);K(t,H.loadedClass);Q(t,H.loadingClass);V(t,L);X(t,"lazyloaded")};var a=te(B);var L=function(e){a({target:e.target})};var T=function(t,i){try{t.contentWindow.location.replace(i)}catch(e){t.src=i}};var F=function(e){var t;var i=e[$](H.srcsetAttr);if(t=H.customMedia[e[$]("data-media")||e[$]("media")]){e.setAttribute("media",t)}if(i){e.setAttribute("srcset",i)}};var s=te(function(t,e,i,a,r){var n,s,l,o,u,f;if(!(u=X(t,"lazybeforeunveil",e)).defaultPrevented){if(a){if(i){K(t,H.autosizesClass)}else{t.setAttribute("sizes",a)}}s=t[$](H.srcsetAttr);n=t[$](H.srcAttr);if(r){l=t.parentNode;o=l&&j.test(l.nodeName||"")}f=e.firesLoad||"src"in t&&(s||n||o);u={target:t};K(t,H.loadingClass);if(f){clearTimeout(c);c=I(x,2500);V(t,L,true)}if(o){G.call(l.getElementsByTagName("source"),F)}if(s){t.setAttribute("srcset",s)}else if(n&&!o){if(d.test(t.nodeName)){T(t,n)}else{t.src=n}}if(r&&(s||o)){Y(t,{src:n})}}if(t._lazyRace){delete t._lazyRace}Q(t,H.lazyClass);ee(function(){var e=t.complete&&t.naturalWidth>1;if(!f||e){if(e){K(t,"ls-is-cached")}B(u);t._lazyCache=true;I(function(){if("_lazyCache"in t){delete t._lazyCache}},9)}if(t.loading=="lazy"){N--}},true)});var R=function(e){if(e._lazyRace){return}var t;var i=n.test(e.nodeName);var a=i&&(e[$](H.sizesAttr)||e[$]("sizes"));var r=a=="auto";if((r||!m)&&i&&(e[$]("src")||e.srcset)&&!e.complete&&!J(e,H.errorClass)&&J(e,H.lazyClass)){return}t=X(e,"lazyunveilread").detail;if(r){re.updateElem(e,true,e.offsetWidth)}e._lazyRace=true;N++;s(e,t,r,a,i)};var r=ae(function(){H.loadMode=3;i()});var l=function(){if(H.loadMode==3){H.loadMode=2}r()};var o=function(){if(m){return}if(f.now()-e<999){I(o,999);return}m=true;H.loadMode=3;i();q("scroll",l,true)};return{_:function(){e=f.now();k.elements=D.getElementsByClassName(H.lazyClass);v=D.getElementsByClassName(H.lazyClass+" "+H.preloadClass);q("scroll",i,true);q("resize",i,true);q("pageshow",function(e){if(e.persisted){var t=D.querySelectorAll("."+H.loadingClass);if(t.length&&t.forEach){U(function(){t.forEach(function(e){if(e.complete){R(e)}})})}}});if(u.MutationObserver){new MutationObserver(i).observe(O,{childList:true,subtree:true,attributes:true})}else{O[P]("DOMNodeInserted",i,true);O[P]("DOMAttrModified",i,true);setInterval(i,999)}q("hashchange",i,true);["focus","mouseover","click","load","transitionend","animationend"].forEach(function(e){D[P](e,i,true)});if(/d$|^c/.test(D.readyState)){o()}else{q("load",o);D[P]("DOMContentLoaded",i);I(o,2e4)}if(k.elements.length){t();ee._lsFlush()}else{i()}},checkElems:i,unveil:R,_aLSL:l}}(),re=function(){var i;var n=te(function(e,t,i,a){var r,n,s;e._lazysizesWidth=a;a+="px";e.setAttribute("sizes",a);if(j.test(t.nodeName||"")){r=t.getElementsByTagName("source");for(n=0,s=r.length;n<s;n++){r[n].setAttribute("sizes",a)}}if(!i.detail.dataAttr){Y(e,i.detail)}});var a=function(e,t,i){var a;var r=e.parentNode;if(r){i=s(e,r,i);a=X(e,"lazybeforesizes",{width:i,dataAttr:!!t});if(!a.defaultPrevented){i=a.detail.width;if(i&&i!==e._lazysizesWidth){n(e,r,a,i)}}}};var e=function(){var e;var t=i.length;if(t){e=0;for(;e<t;e++){a(i[e])}}};var t=ae(e);return{_:function(){i=D.getElementsByClassName(H.autosizesClass);q("resize",t)},checkElems:t,updateElem:a}}(),t=function(){if(!t.i&&D.getElementsByClassName){t.i=true;re._();e._()}};return I(function(){H.init&&t()}),k={cfg:H,autoSizer:re,loader:e,init:t,uP:Y,aC:K,rC:Q,hC:J,fire:X,gW:s,rAF:ee}}(e,e.document,Date);e.lazySizes=t,"object"==typeof module&&module.exports&&(module.exports=t)}("undefined"!=typeof window?window:{});'},334:function(e,t,i){i(11)(i(335))},335:function(e,t){e.exports='/*! lazysizes - v5.2.2 */\n\n!function(e,t){var i=function(){t(e.lazySizes),e.removeEventListener("lazyunveilread",i,!0)};t=t.bind(null,e,e.document),"object"==typeof module&&module.exports?t(require("lazysizes")):"function"==typeof define&&define.amd?define(["lazysizes"],t):e.lazySizes?i():e.addEventListener("lazyunveilread",i,!0)}(window,function(o,r,e){"use strict";var s,t,i,n,d,c,a,u,f,l,m,h,p;function g(){this.ratioElems=r.getElementsByClassName("lazyaspectratio"),this._setupEvents(),this.processImages()}o.addEventListener&&(s=Array.prototype.forEach,d=/^picture$/i,a="img["+(c="data-aspectratio")+"]",u=function(e){return o.matchMedia?(u=function(e){return!e||(matchMedia(e)||{}).matches})(e):o.Modernizr&&Modernizr.mq?!e||Modernizr.mq(e):!e},f=e.aC,l=e.rC,m=e.cfg,g.prototype={_setupEvents:function(){function t(e){e.naturalWidth<36?n.addAspectRatio(e,!0):n.removeAspectRatio(e,!0)}function e(){n.processImages()}var i,n=this;function a(){s.call(n.ratioElems,t)}r.addEventListener("load",function(e){e.target.getAttribute&&e.target.getAttribute(c)&&t(e.target)},!0),addEventListener("resize",function(){clearTimeout(i),i=setTimeout(a,99)}),r.addEventListener("DOMContentLoaded",e),addEventListener("load",e)},processImages:function(e){for(var t=("length"in(e=e||r)&&!e.nodeName?e:e.querySelectorAll(a)),i=0;i<t.length;i++)36<t[i].naturalWidth?this.removeAspectRatio(t[i]):this.addAspectRatio(t[i])},getSelectedRatio:function(e){var t,i,n,a,o,r=e.parentNode;if(r&&d.test(r.nodeName||""))for(t=0,i=(n=r.getElementsByTagName("source")).length;t<i;t++)if(a=n[t].getAttribute("data-media")||n[t].getAttribute("media"),m.customMedia[a]&&(a=m.customMedia[a]),u(a)){o=n[t].getAttribute(c);break}return o||e.getAttribute(c)||""},parseRatio:(h=/^\\s*([+\\d\\.]+)(\\s*[\\/x]\\s*([+\\d\\.]+))?\\s*$/,p={},function(e){var t;return!p[e]&&(t=e.match(h))&&(t[3]?p[e]=t[1]/t[3]:p[e]=+t[1]),p[e]}),addAspectRatio:function(e,t){var i,n=e.offsetWidth,a=e.offsetHeight;t||f(e,"lazyaspectratio"),n<36&&a<=0?(n||a&&o.console)&&console.log("Define width or height of image, so we can calculate the other dimension"):(i=this.getSelectedRatio(e),(i=this.parseRatio(i))&&(n?e.style.height=n/i+"px":e.style.width=a*i+"px"))},removeAspectRatio:function(e){l(e,"lazyaspectratio"),e.style.height="",e.style.width="",e.removeAttribute(c)}},(i=function(){(n=o.jQuery||o.Zepto||o.shoestring||o.$)&&n.fn&&!n.fn.imageRatio&&n.fn.filter&&n.fn.add&&n.fn.find?n.fn.imageRatio=function(){return t.processImages(this.find(a).add(this.filter(a))),this}:n=!1})(),setTimeout(i),t=new g,o.imageRatio=t,"object"==typeof module&&module.exports?module.exports=t:"function"==typeof define&&define.amd&&define(t))});'},98:function(e,t,i){"use strict";i(99),i(133),i(134),i(135),i(136),i(137),i(138);function n(){return function(e){var t=null;if(document.cookie&&""!=document.cookie)for(var i=document.cookie.split(";"),n=0;n<i.length;n++){var r=jQuery.trim(i[n]);if(r.substring(0,e.length+1)==e+"="){t=decodeURIComponent(r.substring(e.length+1));break}}return t}("csrftoken")}function r(e,t){for(var i=0;i<t.length;i++){var n=t[i];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}var a=function(){function e(){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.init()}var t,i,a;return t=e,(i=[{key:"init",value:function(){this.scrollToTop(),this.csrfToken(),this.siteMessages()}},{key:"scrollToTop",value:function(){$(".scroll-top").on("click",(function(e){return e&&(e.preventDefault(),e.stopPropagation()),$("html,body").animate({scrollTop:0},450),!1}))}},{key:"csrfToken",value:function(){$.ajaxSetup({beforeSend:function(e,t){var i;i=t.type,/^(GET|HEAD|OPTIONS|TRACE)$/.test(i)||this.crossDomain||e.setRequestHeader("X-CSRFToken",n())},data:{csrfmiddlewaretoken:n()}})}},{key:"siteMessages",value:function(){$(".site-messages .alert").each((function(){var e=$(this).attr("id");document.cookie.split(";").some((function(t){return 0==t.trim().indexOf(e)}))?$(this).hide():$(this).show(),$(this).find("button").on("click",(function(){document.cookie=e+"=closed; max-age=86400; path=/"}))}))}}])&&r(t.prototype,i),a&&r(t,a),e}();function o(e,t){for(var i=0;i<t.length;i++){var n=t[i];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}var s=function(){function e(){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.init()}var t,i,n;return t=e,(i=[{key:"init",value:function(){this.svg()}},{key:"svg",value:function(){inlineSVG.init({svgSelector:"img.inline-svg",initClass:"js-inlinesvg"})}}])&&o(t.prototype,i),n&&o(t,n),e}(),l=i(30);function u(e,t){for(var i=0;i<t.length;i++){var n=t[i];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}var c=function(){function e(){!function(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}(this,e),this.init()}var t,i,n;return t=e,(i=[{key:"init",value:function(){this.stickyHeader(),this.searchBar()}},{key:"stickyHeader",value:function(){$(window).on("scroll",(function(e){$(window).scrollTop()>=100?$("header#site-header").addClass("site-header__scrolled"):$("header#site-header").removeClass("site-header__scrolled")}))}},{key:"searchBar",value:function(){$("[data-trigger-search-bar]").on("click",(function(e){var t;e.preventDefault(),t=$("#search-form").hasClass("visible"),$("#search-form").toggleClass("visible"),$("header#site-header").toggleClass("inverted-search-bar"),t||$("#search-form input.search-terms").focus()})),$(document).keyup((function(e){27===e.keyCode&&$(".nav-search-triggers__close").click()}))}}])&&u(t.prototype,i),n&&u(t,n),e}();new a,new s,new l.b,new c}});