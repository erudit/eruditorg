!function(t){function e(e){for(var i,r,c=e[0],s=e[1],l=e[2],d=0,f=[];d<c.length;d++)r=c[d],Object.prototype.hasOwnProperty.call(o,r)&&o[r]&&f.push(o[r][0]),o[r]=0;for(i in s)Object.prototype.hasOwnProperty.call(s,i)&&(t[i]=s[i]);for(u&&u(e);f.length;)f.shift()();return a.push.apply(a,l||[]),n()}function n(){for(var t,e=0;e<a.length;e++){for(var n=a[e],i=!0,c=1;c<n.length;c++){var s=n[c];0!==o[s]&&(i=!1)}i&&(a.splice(e--,1),t=r(r.s=n[0]))}return t}var i={},o={2:0},a=[];function r(e){if(i[e])return i[e].exports;var n=i[e]={i:e,l:!1,exports:{}};return t[e].call(n.exports,n,n.exports,r),n.l=!0,n.exports}r.m=t,r.c=i,r.d=function(t,e,n){r.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},r.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},r.t=function(t,e){if(1&e&&(t=r(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(r.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var i in t)r.d(n,i,function(e){return t[e]}.bind(null,i));return n},r.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return r.d(e,"a",e),e},r.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},r.p="";var c=window.webpackJsonp=window.webpackJsonp||[],s=c.push.bind(c);c.push=e,c=c.slice();for(var l=0;l<c.length;l++)e(c[l]);var u=s;a.push([139,0]),n()}({137:function(t,e){t.exports=jQuery},138:function(t,e,n){var i;i=function(){return function(t){var e={};function n(i){if(e[i])return e[i].exports;var o=e[i]={exports:{},id:i,loaded:!1};return t[i].call(o.exports,o,o.exports,n),o.loaded=!0,o.exports}return n.m=t,n.c=e,n.p="dist/",n(0)}([function(t,e){"use strict";Object.defineProperty(e,"__esModule",{value:!0}),e.default=function(t){if("undefined"==typeof document)return t;var e=document.createElement("p").style,n=["ms","O","Moz","Webkit"];if(""===e[t])return t;t=t.charAt(0).toUpperCase()+t.slice(1);for(var i=n.length;i--;)if(""===e[n[i]+t])return n[i]+t},t.exports=e.default}])},t.exports=i()},139:function(t,e,n){n(353),t.exports=n(338)},335:function(t,e,n){(function(e){var i=n(337);e.ScrollSpy=t.exports=i}).call(this,n(336))},336:function(t,e){var n;n=function(){return this}();try{n=n||new Function("return this")()}catch(t){"object"==typeof window&&(n=window)}t.exports=n},337:function(t,e){function n(t,e){this.doc=document,this.wrapper="string"==typeof t?this.doc.querySelector(t):t,this.nav=this.wrapper.querySelectorAll(e.nav),this.contents=[],this.win=window,this.winH=this.win.innerHeight,this.className=e.className,this.callback=e.callback,this.init()}n.prototype.init=function(){this.contents=this.getContents(),this.attachEvent()},n.prototype.getContents=function(){for(var t=[],e=0,n=this.nav.length;e<n;e++){var i=this.nav[e].href;t.push(this.doc.getElementById(i.split("#")[1]))}return t},n.prototype.attachEvent=function(){var t,e;this.win.addEventListener("load",function(){this.spy(this.callback)}.bind(this)),this.win.addEventListener("scroll",function(){t&&clearTimeout(t);var e=this;t=setTimeout((function(){e.spy(e.callback)}),10)}.bind(this)),this.win.addEventListener("resize",function(){e&&clearTimeout(e);var t=this;e=setTimeout((function(){t.spy(t.callback)}),10)}.bind(this))},n.prototype.spy=function(t){var e=this.getElemsViewState();this.markNav(e),"function"==typeof t&&t(e)},n.prototype.getElemsViewState=function(){for(var t=[],e=[],n=[],i=0,o=this.contents.length;i<o;i++){var a=this.contents[i],r=this.isInView(a);r?t.push(a):e.push(a),n.push(r)}return{inView:t,outView:e,viewStatusList:n}},n.prototype.isInView=function(t){var e=this.winH,n=this.doc.documentElement.scrollTop||this.doc.body.scrollTop,i=n+e,o=t.getBoundingClientRect().top+n,a=o+t.offsetHeight;return o<i&&a>n},n.prototype.markNav=function(t){for(var e=this.nav,n=!1,i=0,o=e.length;i<o;i++)t.viewStatusList[i]&&!n?(n=!0,e[i].classList.add(this.className)):e[i].classList.remove(this.className)},t.exports=n},338:function(t,e,n){},353:function(t,e,n){"use strict";n.r(e);n(91);var i=n(50),o=n(39),a={init:function(){Object(o.a)()}},r={init:function(){var t=$("#id_search"),e=$("#id_add_q_field");$("#id_disciplines").select2(),$("#id_languages").select2(),$("#id_journals").select2(),$("#id_advanced_q_wrapper [data-q-id]").each((function(){$(this).find("#id_advanced_search_term"+$(this).data("q-id")).val()&&($(this).show(),$(this).data("q-used",!0))})),e.click((function(t){t.preventDefault();var n=$("#id_advanced_q_wrapper [data-q-id]");n.each((function(){if(!$(this).data("q-used"))return $(this).fadeIn(),$(this).data("q-used",!0),!1})),5==n.filter((function(){return 1==$(this).data("q-used")})).length&&e.hide()})),$(".remove-qbox").click((function(t){t.preventDefault();var n=$(this).parents("[data-q-id]");n.data("q-used",!1),n.find("#id_advanced_search_term"+n.data("q-id")).val(""),n.find("#id_advanced_search_operator"+n.data("q-id")).prop("selectedIndex",0),n.find("#id_advanced_search_field"+n.data("q-id")).prop("selectedIndex",0),n.hide(),$("#id_advanced_q_wrapper [data-q-id]").filter((function(){return 1==$(this).data("q-used")})).length<5&&e.show()})),t.submit((function(t){$(".advanced-search-popup-error").hide(),$("#id_basic_search_term").val()||($("#div_id_basic_search_term .advanced-search-popup-error").show(),t.preventDefault())})),$(".remove-search").click((function(t){var e=$(this).parents(".saved-search");$.ajax({type:"POST",url:Urls["public:search:remove_search"](e.data("uuid"))}).done((function(){e.remove()})),t.preventDefault()}))}};function c(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}function s(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var l=function(){function t(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};c(this,t);var n={documentAddDataAttribute:"citation-save",documentRemoveDataAttribute:"citation-remove",documentButtonSelector:"[data-citation-list-button]",documentIdDataAttribute:"document-id",documentIsSavedDataAttribute:"is-in-citation-list"};this.options=Object.assign(n,e),this.addButtonSelector="[data-"+this.options.documentAddDataAttribute+"]",this.removeButtonSelector="[data-"+this.options.documentRemoveDataAttribute+"]"}var e,n,i;return e=t,(n=[{key:"save",value:function(t){var e=this,n=t.data(this.options.documentIdDataAttribute),i=t.attr("id");$.ajax({type:"POST",url:Urls["public:citations:add_citation"](),data:{document_id:n}}).done((function(){t.data(e.options.documentIsSavedDataAttribute,!0),$("[data-"+e.options.documentAddDataAttribute+'="#'+i+'"]').hide(),$("[data-"+e.options.documentRemoveDataAttribute+'="#'+i+'"]').show()}))}},{key:"remove",value:function(t){var e=this,n=t.data(this.options.documentIdDataAttribute),i=t.attr("id");$.ajax({type:"POST",url:Urls["public:citations:remove_citation"](),data:{document_id:n}}).done((function(){t.data(e.options.documentIsSavedDataAttribute,!1),$("[data-"+e.options.documentAddDataAttribute+'="#'+i+'"]').show(),$("[data-"+e.options.documentRemoveDataAttribute+'="#'+i+'"]').hide()}))}},{key:"init",value:function(){var t=this;$(this.addButtonSelector).on("click",(function(e){var n=$($(e.currentTarget).data(t.options.documentAddDataAttribute));t.save(n),e.preventDefault()})),$(this.removeButtonSelector).on("click",(function(e){var n=$($(e.currentTarget).data(t.options.documentRemoveDataAttribute));t.remove(n),e.preventDefault()})),$("[data-"+this.options.documentIdDataAttribute+"]").each((function(e,n){var i=$(n).attr("id");1==$(n).data(t.options.documentIsSavedDataAttribute)?($("[data-"+t.options.documentAddDataAttribute+'="#'+i+'"]').hide(),$("[data-"+t.options.documentRemoveDataAttribute+'="#'+i+'"]').show()):($("[data-"+t.options.documentAddDataAttribute+'="#'+i+'"]').show(),$("[data-"+t.options.documentRemoveDataAttribute+'="#'+i+'"]').hide())}))}}])&&s(e.prototype,n),i&&s(e,i),t}();var u=function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),e.magnificPopup({mainClass:"mfp-fade",removalDelay:750,type:"ajax",closeOnBgClick:!0,closeBtnInside:!0,items:{src:e.data("modal-id"),type:"inline"}})},d={facebook:function(t,e){var n={t:e,u:encodeURI(t)},i="https://www.facebook.com/sharer/sharer.php?"+$.param(n),o=($(window).width()-575)/2,a="status=1,width=575,height=400,top="+($(window).height()-400)/2+",left="+o;window.open(i,"facebook",a)},twitter:function(t,e){var n={text:e,url:encodeURI(t)},i="https://twitter.com/intent/tweet?"+$.param(n),o=($(window).width()-575)/2,a="status=1,width=575,height=400,top="+($(window).height()-400)/2+",left="+o;window.open(i,"twitter",a)},linkedin:function(t,e){var n={mini:!0,title:e,url:encodeURI(t),summary:"",source:""},i="https://www.linkedin.com/shareArticle?"+$.param(n),o=($(window).width()-575)/2,a="status=1,width=575,height=400,top="+($(window).height()-400)/2+",left="+o;window.open(i,"linkedin",a)},email:function(t,e,n){var i="mailto:?subject=Érudit%20–%20"+encodeURIComponent(e.replace(/^\s+|\s+$/g,""))+"&body="+encodeURIComponent((n.replace(/^\s+|\s+$/g,"")||"")+"\n\n"+t);document.location.href=i}};function f(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var p=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.el=e,this.title=e.data("title")||document.title,this.title=this.title.replace(/\s+/g," "),this.url=e.data("share-url")||window.location.href,this.citation_text=$(e.data("cite")).text().replace(/\s+/g," "),this.init()}var e,n,i;return e=t,(n=[{key:"init",value:function(){var t=this;this.el.magnificPopup({mainClass:"mfp-fade",removalDelay:750,closeOnBgClick:!0,closeBtnInside:!0,showCloseBtn:!1,items:{src:'<div class="modal share-modal col-lg-3 col-md-5 col-sm-6 col-xs-12 col-centered">                <div class="panel">                  <header class="panel-heading">                    <h2 class="h4 panel-title text-center">'+gettext("Partager ce document")+'</h2>                  </header>                  <div class="panel-body share-modal--body">                    <ul class="unstyled">                      <li><button id="share-email" class="btn btn-primary btn-block"><i class="icon ion-ios-mail"></i> '+gettext("Courriel")+'</button></li>                      <li><button id="share-twitter" class="btn btn-primary btn-block"><i class="icon ion-logo-twitter"></i> Twitter</button></li>                      <li><button id="share-facebook" class="btn btn-primary btn-block"><i class="icon ion-logo-facebook"></i> Facebook</button></li>                      <li><button id="share-linkedin" class="btn btn-primary btn-block"><i class="icon ion-logo-linkedin"></i> LinkedIn</button></li>                    </ul>                  </div>                </div>              </div>',type:"inline"},callbacks:{open:function(){var e=$($.magnificPopup.instance.content);e.on("click","#share-email",(function(e){return e.preventDefault(),d.email(t.url,t.title,t.citation_text.replace(/(\r\n|\n|\r)/gm,"")),!1})),e.on("click","#share-twitter",(function(e){return e.preventDefault(),d.twitter(t.url),!1})),e.on("click","#share-facebook",(function(e){return e.preventDefault(),d.facebook(t.url,t.title),!1})),e.on("click","#share-linkedin",(function(e){return e.preventDefault(),d.linkedin(t.url,t.title),!1}))},close:function(){$($.magnificPopup.instance.content).off("click")}}})}}])&&f(e.prototype,n),i&&f(e,i),t}();function h(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var v=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.el=e,this.init()}var e,n,i;return e=t,(n=[{key:"init",value:function(){this.el.on("click",".tool-download",this.download),this.citation=new u(this.el.find(".tool-cite")),this.share=new p(this.el.find(".tool-share"))}},{key:"download",value:function(t){return t.preventDefault(),window.open($(this).data("href")),!1}}])&&h(e.prototype,n),i&&h(e,i),t}(),m={init:function(){var t=$("#id_search_results_metadata");this.toolbox(),this.saved_citations=new l,this.saved_citations.init(),$("#id_save_search").click((function(e){var n=$("form#id-search");$.ajax({type:"POST",url:Urls["public:search:add_search"](),data:{querystring:n.serialize(),results_count:t.data("results-count")}}).done((function(){$("#id_save_search").addClass("disabled"),$("#id_save_search").text(gettext("Résultats sauvegardés !"))})),e.preventDefault()})),$("#id_page_size,#id_sort_by").change((function(t){var e=$("form#id-search");window.location.href="?"+e.serialize()}))},toolbox:function(){$("#search-results .result .toolbox").each((function(){new v($(this))}))}},b=(n(335),n(138)),g=n.n(b),w={"public:login":a,"public:search:advanced-search":r,"public:search:results":m,"public:journal:article_detail":{init:function(){this.article=$("#article_detail"),this.toolbox=new v(this.article),this.saved_citations=new l,this.saved_citations.init(),this.sticky_elements(),this.smooth_scroll(),this.clipboard(),this.scrollspy(),this.display_pdf_based_on_mimetype(),this.lightbox()},sticky_elements:function(){var t=this.article.find(".article-table-of-contents, .toolbox-wrapper"),e=g()("transform");t.css("padding-bottom",20).stick_in_parent({offset_top:20}).first().on("sticky_kit:stick",(function(n){setTimeout((function(){t.css(e,"translate(0, 0)")}),0)})).on("sticky_kit:unstick",(function(n){setTimeout((function(){t.css(e,"translate(0, 0)")}),0)}))},smooth_scroll:function(){var t=this;this.article.on("click",'a[href^="#"]',(function(e){e&&(e.preventDefault(),e.stopPropagation());var n=$(e.currentTarget).attr("href").replace("#","");return!!n&&($("html, body").animate({scrollTop:t.article.find("#"+n).offset().top-10},750),!1)}))},clipboard:function(t){function e(){return t.apply(this,arguments)}return e.toString=function(){return t.toString()},e}((function(){this.article.find(".clipboard-data").on("click",(function(t){return t&&(t.preventDefault(),t.stopPropagation()),clipboard.writeText($(t.currentTarget).attr("href")).then((function(){$(t.currentTarget).addClass("success"),setTimeout((function(){$(t.currentTarget).removeClass("success error")}),3e3)}),(function(){$(t.currentTarget).addClass("error"),setTimeout((function(){$(t.currentTarget).removeClass("success error")}),3e3)})),!1}))})),scrollspy:function(){var t=this.article.find("#article-content")[0],e=this.article.find(".article-table-of-contents .article-table-of-contents--body"),n=e.find("a");if(e.length>0)new ScrollSpy(t,{nav:"nav.article-table-of-contents ul li a",className:"is-inview",callback:function(t){n.hasClass("is-inview")?e.addClass("is-inview"):e.removeClass("is-inview")}});if(e.length>0){console.log("length");new ScrollSpy(t,{nav:".article-table-of-contents--body ol li a",className:"is-insubview"})}},display_pdf_based_on_mimetype:function(){var t=!1;if(void 0!==navigator.mimeTypes["application/pdf"])t=!0;else{var e=navigator.userAgent.match(/Firefox\/(\d+\.\d+)/);e&&e[1]>19&&(t=!0)}t?($("#pdf-download").hide(),$("#pdf-download-menu-link").hide()):($("#pdf-viewer").hide(),$("#pdf-viewer-menu-link").hide())},lightbox:function(){$(".lightbox").magnificPopup({type:"image",closeOnContentClick:!0,closeBtnInside:!1,fixedContentPos:!0,mainClass:"mfp-no-margins mfp-with-zoom",prependTo:$(".full-article"),image:{verticalFit:!1,titleSrc:!1,markup:'<div class="mfp-figure"><div class="mfp-close"></div><figure><div class="mfp-top-bar"><div class="mfp-title"></div></div><div class="mfp-img"></div><figcaption><div class="mfp-bottom-bar"><div class="mfp-counter"></div></div></figcaption></figure></div>'},callbacks:{open:function(){var t=$(this.currItem.el).closest(".figure, .tableau"),e=t.closest(".grfigure, .grtableau"),n=e.find(".grfigure-caption"),i=n.find(".no"),o=n.find("div.legende"),a=t.find(".no"),r=t.find(".legende"),c=e.find("div.grfigure-legende"),s=t.find("div.figure-legende"),l=t.find("div.notefigtab"),u=$("<p>").html(t.find(".source").html());$(this.content).find(".mfp-top-bar .mfp-title").prepend(i.clone(),o.clone(),a.clone(),r.clone()),$(this.content).find(".mfp-bottom-bar").prepend(s.clone(),l.clone(),u.clone(),c.clone()),$(this.content).parent(".mfp-content").css("margin-top",$(this.content).find(".mfp-top-bar").height()-20)}},zoom:{enabled:!0,duration:300}})}},"public:journal:issue_detail":{init:function(){this.saved_citations=new l,this.saved_citations.init()}},"public:journal:journal_list":{init:function(){this.smoothScroll(),this.stickyElements(),$("#id_disciplines").select2()},smoothScroll:function(){$("#journal_list_per_names .alpha-nav").on("click","a",(function(t){t.preventDefault(),t.stopPropagation();var e=$(this).attr("href").replace("#","");return $("html, body").animate({scrollTop:$('ul[id="'+e+'"]').offset().top-137},750),!1})),$("#journal_list_per_disciplines .discipline-nav").on("click","a",(function(t){t.preventDefault(),t.stopPropagation();var e=$(this).attr("href").replace("#","");return $("html, body").animate({scrollTop:$('a[id="'+e+'"]').offset().top-100},750),!1}))},stickyElements:function(){$("#journal_list_per_names").length&&$(window).scroll((function(){var t,e,n=$("#journal_list_per_names").offset().top+390;t=n,e=$(".filters"),$(window).scrollTop()>=t?e.addClass("sticky"):e.removeClass("sticky"),function(t){var e=$(".list-header");$(window).scrollTop()>=t?e.addClass("sticky"):e.removeClass("sticky")}(n)}))}},"public:journal:journal_detail":{init:function(){var t=this.find_url_fragment();this.set_active_fragment(t[0],t[1])},find_url_fragment:function(){var t=null,e=null;if(window.location.hash){var n=window.location.hash.substring(1);t=$("#"+(n+"-li")),e=$("#"+n)}return[t,e]},set_active_fragment:function(t,e){t||(t=$('[role="presentation"]').first()),e||(e=$('[role="tabpanel"]').first()),$(t).addClass("active"),$(e).addClass("active")}},"public:citations:list":{init:function(){function t(){var t=$("#citations_list .bib-records .checkbox input[type=checkbox]:checked").length,e={count:t},n=ngettext("%(count)s document sélectionné","%(count)s documents sélectionnés",e.count),i=interpolate(n,e,!0);$(".saved-citations strong").text(i),t?$("#id_selection_tools").show():$("#id_selection_tools").hide()}function e(t){var e=t.data("document-type"),n=$("[data-"+e+"-count]"),i=parseInt(n.data(e+"-count"));if(i-=1){var o={count:i},a=void 0;"scientific-article"===e?a=ngettext("%(count)s article savant","%(count)s articles savants",o.count):"cultural-article"===e?a=ngettext("%(count)s article culturel","%(count)s articles culturels",o.count):"thesis"===e&&(a=ngettext("%(count)s thèse","%(count)s thèses",o.count));var r=interpolate(a,o,!0);n.text(r),n.data(e+"-count",i)}else n.remove()}function n(){var t=new Array;return $("#citations_list .bib-records .checkbox input[type=checkbox]:checked").each((function(){var e=$(this).parents("li.bib-record");t.push(e.data("document-id"))})),t}$(".documents-head input[type=checkbox]").on("change",(function(t){$(this).is(":checked")?$("#citations_list .bib-records .checkbox input[type=checkbox]").each((function(){$(this).prop("checked",!0)})):$("#citations_list .bib-records .checkbox input[type=checkbox]").each((function(){$(this).prop("checked",!1)})),$("#citations_list .bib-records .checkbox input[type=checkbox]").change()})),$("#citations_list .bib-records .checkbox input[type=checkbox]").on("change",t),$("a[data-remove]").click((function(n){n.preventDefault(),function(n){var i=n.data("document-id");$.ajax({type:"POST",url:Urls["public:citations:remove_citation"](),data:{document_id:i}}).done((function(){n.remove(),t(),e(n)}))}($(this).parents("li.bib-record"))})),$("#id_selection_tools a.remove-selection").click((function(i){if(i.preventDefault(),0!=confirm(gettext("Voulez-vous vraiment supprimer votre sélection ?"))){var o=n();$.ajax({type:"POST",url:Urls["public:citations:remove_citation_batch"](),data:{document_ids:o},traditional:!0}).done((function(){$("#citations_list .bib-records .checkbox input[type=checkbox]:checked").each((function(){var n=$(this).parents("li.bib-record");e(n),n.remove(),t()}))}))}})),$("#export_citation_enw").click((function(t){t.preventDefault();var e=n(),i=Urls["public:citations:citation_enw"]()+"?"+$.param({document_ids:e},!0);window.location.href=i})),$("#export_citation_ris").click((function(t){t.preventDefault();var e=n(),i=Urls["public:citations:citation_ris"]()+"?"+$.param({document_ids:e},!0);window.location.href=i})),$("#export_citation_bib").click((function(t){t.preventDefault();var e=n(),i=Urls["public:citations:citation_bib"]()+"?"+$.param({document_ids:e},!0);window.location.href=i})),$("a[data-cite]").each((function(){new u($(this))}))}}},y=new i.a(w);$(document).ready((function(t){y.init()}))},39:function(t,e,n){"use strict";n.d(e,"a",(function(){return o}));n(134),n(135);function i(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}function o(){$("form#id-login-form").validate({rules:{username:{required:!0},password:{required:!0}},messages:{username:gettext("Ce champ est obligatoire."),password:gettext("Ce champ est obligatoire.")}})}var a=function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.previousURL=null,this.modalSelector="#login-modal, #article-login-modal, #journal-login-modal",this.init()}var e,n,a;return e=t,(n=[{key:"init",value:function(){this.modal()}},{key:"modal",value:function(){var t=this;$(this.modalSelector).magnificPopup({mainClass:"mfp-fade",removalDelay:750,type:"ajax",closeOnBgClick:!1,closeBtnInside:!0,ajax:{settings:{beforeSend:function(t){t.setRequestHeader("X-PJAX","true")}}},callbacks:{beforeOpen:function(){t.previousURL=window.location.pathname},open:function(){history.replaceState(null,null,$($.magnificPopup.instance.currItem.el).attr("href")),$("body").addClass("modal-open")},ajaxContentAdded:function(){o()},close:function(){history.replaceState(null,null,t.previousURL),$("body").removeClass("modal-open")}}})}}])&&i(e.prototype,n),a&&i(e,a),t}();e.b=a},50:function(t,e,n){"use strict";function i(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var o=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.controllers=void 0===e?{}:e}var e,n,o;return e=t,(n=[{key:"execAction",value:function(t,e){""!==t&&this.controllers[t]&&"function"==typeof this.controllers[t][e]&&this.controllers[t][e]()}},{key:"init",value:function(){if(document.body){var t=document.body,e=t.getAttribute("data-controller"),n=t.getAttribute("data-action");e&&(this.execAction(e,"init"),this.execAction(e,n))}}}])&&i(e.prototype,n),o&&i(e,o),t}();e.a=o},91:function(t,e,n){"use strict";n(92),n(126),n(127),n(128),n(129),n(130),n(131),n(132),n(133);function i(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var o=function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.init()}var e,n,o;return e=t,(n=[{key:"init",value:function(){this.scrollToTop()}},{key:"scrollToTop",value:function(){$(".scroll-top").on("click",(function(t){return t&&(t.preventDefault(),t.stopPropagation()),$("html,body").animate({scrollTop:0},450),!1}))}}])&&i(e.prototype,n),o&&i(e,o),t}();function a(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var r=function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.init()}var e,n,i;return e=t,(n=[{key:"init",value:function(){this.svg()}},{key:"svg",value:function(){inlineSVG.init({svgSelector:"img.inline-svg",initClass:"js-inlinesvg"})}}])&&a(e.prototype,n),i&&a(e,i),t}(),c=n(39);function s(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var l=function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.init()}var e,n,i;return e=t,(n=[{key:"init",value:function(){this.stickyHeader(),this.searchBar()}},{key:"stickyHeader",value:function(){$(window).on("scroll",(function(t){$(window).scrollTop()>=100?$("header#site-header").addClass("site-header__scrolled"):$("header#site-header").removeClass("site-header__scrolled")}))}},{key:"searchBar",value:function(){$("[data-trigger-search-bar]").on("click",(function(t){var e;t.preventDefault(),e=$("#search-form").hasClass("visible"),$("#search-form").toggleClass("visible"),$("header#site-header").toggleClass("inverted-search-bar"),e||$("#search-form input.search-terms").focus()})),$(document).keyup((function(t){27===t.keyCode&&$(".nav-search-triggers__close").click()}))}}])&&s(e.prototype,n),i&&s(e,i),t}();new o,new r,new c.b,new l;n(136);function u(){return function(t){var e=null;if(document.cookie&&""!=document.cookie)for(var n=document.cookie.split(";"),i=0;i<n.length;i++){var o=jQuery.trim(n[i]);if(o.substring(0,t.length+1)==t+"="){e=decodeURIComponent(o.substring(t.length+1));break}}return e}("csrftoken")}$.ajaxSetup({beforeSend:function(t,e){var n;n=e.type,/^(GET|HEAD|OPTIONS|TRACE)$/.test(n)||this.crossDomain||t.setRequestHeader("X-CSRFToken",u())},data:{csrfmiddlewaretoken:u()}})}});