{% load adv_cache i18n public_journal_tags staticfiles waffle_tags %}<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:v="variables-node" version="2.0">
  <xsl:output method="html" indent="yes" encoding="UTF-8"/>

  <!--=========== VARIABLES & PARAMETERS ===========-->
  <!-- possible values for cover - 'no', 'coverpage.jpg', 'no-image' -->
  <xsl:variable name="iderudit" select="article/@idproprio"/>
  <xsl:variable name="doi" select="normalize-space(article/admin/infoarticle/idpublic[@scheme = 'doi'])"/>
  <xsl:variable name="typeudoc">
    <xsl:choose>
      <xsl:when test="article/@typeart='article'">
        <xsl:value-of select="'article'" />
      </xsl:when>
      <xsl:when test="article/@typeart='compte rendu' or article/@typeart='compterendu'">
        <xsl:value-of select="'compterendu'" />
      </xsl:when>
      <xsl:when test="starts-with(article/@typeart, 'note')">
        <xsl:value-of select="'note'" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="'autre'" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="titreAbrege" select="article/admin/revue/titrerevabr"/>
  <xsl:variable name="uriStart">https://id.erudit.org/iderudit/</xsl:variable>
  <xsl:variable name="doiStart">https://doi.org/</xsl:variable>

  <v:variables>
    {% for imid, infoimg in article.fedora_object.infoimg_dict.items %}
    <v:variable n="plgr-{{ imid }}" value="{{ infoimg.plgr }}" />
    {% endfor %}
  </v:variables>
  <xsl:variable name="vars" select="document('')//v:variables/v:variable" />

  <!-- Savante, culturelle, ... -->
  <xsl:param name="typecoll" />

  <xsl:template match="/">
    <div class="article-wrapper">
      <xsl:apply-templates select="article"/>
    </div>
  </xsl:template>

  <xsl:template match="article">

    <!-- main header -->
    <header class="main-header doc-head" id="article-header">

      <div class="row article-title-group">

        <div class="col-md-9">
          <xsl:if test="liminaire/grtitre/surtitre">
            <p class="main-header__meta">
              <xsl:apply-templates select="liminaire/grtitre/surtitre" mode="title"/>
              <xsl:apply-templates select="liminaire/grtitre/surtitreparal" mode="title"/>
            </p>
          </xsl:if>
          <h1 class="doc-head__title">
            <xsl:apply-templates select="liminaire/grtitre/titre | liminaire/grtitre/sstitre" mode="title"/>
            <xsl:apply-templates select="liminaire/grtitre/titreparal | liminaire/grtitre/sstitreparal" mode="title"/>
            <xsl:apply-templates select="liminaire/grtitre/trefbiblio" mode="title"/>
            {% if only_display == 'summary' %}<span><em>[{% trans 'Notice' %}]</em></span>{% endif %}
            {% if only_display == 'biblio' %}<span><em>[{% trans 'Bibliographie' %}]</em></span>{% endif %}
          </h1>
          <xsl:if test="liminaire/grauteur">
            <ul class="grauteur doc-head__authors">
              <xsl:apply-templates select="liminaire/grauteur/auteur[not(contribution[@typecontrib != 'aut'])]" mode="author"/>
            </ul>
          </xsl:if>
          <xsl:if test="liminaire/grauteur/auteur/contribution or liminaire/grauteur/auteur/affiliation or liminaire/grauteur/auteur/courriel or liminaire/grauteur/auteur/siteweb or liminaire/grauteur/auteur/nompers/suffixe">
            <div class="akkordion doc-head__more-info" data-akkordion-single="true">
              <p class="akkordion-title">{% trans '…plus d’informations' %} <span class="icon ion-ios-arrow-down"></span></p>
              <ul class="akkordion-content unstyled">
                <xsl:apply-templates select="liminaire/grauteur/auteur" mode="affiliations"/>
              </ul>
            </div>
          </xsl:if>
          <div class="row">
            <div class="col-sm-8">
              <xsl:apply-templates select="liminaire/notegen"/>
              {% if not content_access_granted and not only_display %}
              <div class="alert">
                <p>
                  {% blocktrans trimmed with code=article.issue.journal.code %}
                  L’accès aux articles des numéros courants de cette revue est réservé aux abonnés. Pour accéder aux numéros d’archives disponibles en libre accès, consultez l’<a href="https://www.erudit.org/fr/revues/{{ code }}">historique des numéros</a>.
                  {% endblocktrans %}
                  {% url 'public:auth:landing' as login_url %}
                  {% if request.user.is_anonymous %}
                  <br/><br/>
                  {% blocktrans %}
                  Si vous détenez un abonnement individuel à cette revue, veuillez vous identifier <a href="{{ login_url }}" id="article-login-modal" title="Se connecter au tableau de bord">en vous connectant</a>.
                  {% endblocktrans %}
                  {% endif %}
                  <br/><br/>
                  {% if journal_info.subscription_email or journal_info.phone %}
                    {% blocktrans trimmed with journal=article.issue.journal.name email=journal_info.subscription_email phone=journal_info.phone %}
                    Si vous souhaitez vous abonner à titre individuel, et/ou à la version papier, nous vous invitons à communiquer directement avec l’équipe de <em>{{ journal }}</em> à l’adresse <a href="mailto:{{ email }}?subject=Abonnement%20à%20la%20revue%20{{ journal }}">{{ email }}</a> ou par téléphone au {{ phone }}.
                    {% endblocktrans %}
                  {% else %}
                    {% blocktrans trimmed with journal=article.issue.journal.name %}
                    Pour plus d’informations, veuillez communiquer avec nous à l’adresse <a href="mailto:client@erudit.org?subject=Revue%20{{ journal }} – Accès aux articles">client@erudit.org</a>.
                    {% endblocktrans %}
                  {% endif %}
                  <strong>
                    {% if not article.abstracts and can_display_first_pdf_page %}
                    <br/><br/>
                    {% trans "Seule la première page du PDF sera affichée." %}
                    {% elif article.abstracts %}
                    <br/><br/>
                    {% trans "Seul le résumé sera affiché." %}
                    {% elif article.issue.journal.is_scientific %}
                    <br/><br/>
                    {% trans "Seuls les 600 premiers mots du texte seront affichés." %}
                    {% endif %}
                  </strong>
                </p>
              </div>
              {% endif %}
              {% if not article.publication_allowed %}
              <div class="alert">
                <p>
                  {% trans 'Le contenu de ce document est inaccessible en raison du droit d’auteur.' %}
                </p>
              </div>
              {% endif %}
            </div>
          </div>
        </div>

        <!-- issue cover image or journal logo -->
        <div class="col-md-3">
          <a href="{% url 'public:journal:issue_detail' article.issue.journal.code article.issue.volume_slug article.issue.localidentifier %}" title="{% blocktrans with journal=article.issue.journal.name %}Consulter ce numéro de la revue {{ journal|escape }}{% endblocktrans %}">
            {% if article.issue.has_coverpage %}
            <div class="doc-head__img coverpage">
              <img src="{% url 'public:journal:issue_coverpage' article.issue.journal.code article.issue.volume_slug article.issue.localidentifier %}" class="img-responsive" alt="{% trans 'Couverture de' %} {% if article.issue.html_title %}{{ article.issue.html_title|escape }}, {% endif %}{{ article.issue.volume_title_with_pages|escape }}, {{ article.issue.journal.name|escape }}" />
            </div>
            {% else %}
            <div class="doc-head__img logo">
              <img src="{% url 'public:journal:journal_logo' article.issue.journal.code %}" class="img-responsive" alt="{% trans 'Logo de' %} {{ article.issue.journal.name|escape }}" />
            </div>
            {% endif %}
          </a>
          {% if only_display %}
          <a href="{% url 'public:journal:article_detail' journal_code=article.issue.journal.code issue_slug=article.issue.volume_slug issue_localid=article.issue.localidentifier localid=article.localidentifier %}" class="btn btn-primary btn-full-text">{% trans "Lire le texte intégral" %} <span class="ion ion-arrow-right-c"></span></a>
          {% endif %}
        </div>
      </div>

      <div class="row">
        <!-- article metadata -->
        <div class="col-sm-6 doc-head__metadata">
          <xsl:apply-templates select="liminaire/erratum"/>
          <xsl:apply-templates select="admin/histpapier"/>
          <p>{% trans "Diffusion numérique&#160;" %}: {{ article.issue.date_published }}
          <dl class="mono-space idpublic">
            <dt>URI</dt>
            <dd>
              <span class="hint--top hint--no-animate" data-hint="{% blocktrans %}Cliquez pour copier l'URI de cet article.{% endblocktrans %}">
                <a href="https://id.erudit.org/iderudit/{{ article.localidentifier }}" class="clipboard-data">
                  https://id.erudit.org/iderudit/{{ article.localidentifier }}
                  <span class="clipboard-msg clipboard-success">{% trans "adresse copiée" %}</span>
                  <span class="clipboard-msg clipboard-error">{% trans "une erreur s'est produite" %}</span>
                </a>
              </span>
            </dd>

            <xsl:if test="$doi">
              <dt>DOI</dt>
              <dd>
                <span class="hint--top hint--no-animate" data-hint="{% blocktrans %}Cliquez pour copier le DOI de cet article.{% endblocktrans %}">
                  <a href="{$doiStart}{$doi}" class="clipboard-data">
                    <xsl:value-of select="$doiStart"/><xsl:value-of select="$doi"/>
                    <span class="clipboard-msg clipboard-success">{% trans "adresse copiée" %}</span>
                    <span class="clipboard-msg clipboard-error">{% trans "une erreur s'est produite" %}</span>
                  </a>
                </span>
              </dd>
            </xsl:if>
          </dl>
          </p>
        </div>

        <!-- journal metadata -->
        <div class="col-sm-6 doc-head__metadata">
          <p>
            {% blocktrans %}<xsl:apply-templates select="../article/@typeart"/> de la revue{% endblocktrans %}
            <a href="{{ request.is_secure|yesno:'https,http' }}://{{ request.site.domain }}{% url 'public:journal:journal_detail' article.issue.journal.code %}"><xsl:value-of select="admin/revue/titrerev"/></a>
            {# Peer review seal #}
            {% if article.issue.journal.type.code == 'S' and article.erudit_object.get_article_type == 'article' %}
            <xsl:text>&#160;</xsl:text>
            <span class="hint--bottom-left hint--no-animate" data-hint="{% trans 'Tous les articles de cette revue sont soumis à un processus d’évaluation par les pairs.' %}">
              <i class="icon ion-ios-checkmark-circle" size="small"></i>
            </span>
            {% endif %}
          </p>
          <xsl:if test="../article/@typeart = 'compterendu'">
            <p><small>{% trans "Ce document est le compte-rendu d'une autre oeuvre tel qu'un livre ou un film. L'oeuvre originale discutée ici n'est pas disponible sur cette plateforme." %}</small></p>
          </xsl:if>
          <p class="refpapier">
            <xsl:apply-templates select="admin/numero" mode="refpapier"/>
            <xsl:if test="admin/infoarticle/pagination">
              <xsl:apply-templates select="admin/infoarticle/pagination"/>
            </xsl:if>
            <xsl:apply-templates select="admin/numero/grtheme/theme" mode="refpapier"/>
          </p>
          {% if content_access_granted and subscription_type == 'individual' %}
          <p><strong>{% trans "Vous êtes abonné à cette revue." %}</strong></p>
          {% endif %}
          <xsl:apply-templates select="admin/droitsauteur"/>
        </div>
      </div>
    </header>

    <div id="article-content" class="row article-content">

      {# Article navigation arrows #}
      {% include "public/journal/partials/article_detail_toc_nav.html" %}

      <xsl:if test="//corps">
        <!-- article outline -->
        <nav class="hidden-xs hidden-sm hidden-md col-md-3 article-table-of-contents" role="navigation">
          <h2>{% trans "Plan de l’article" %}</h2>
          <ul class="unstyled">
            <li>
              <a href="#article-header">
                <em>{% trans "Retour au début" %}</em>
              </a>
            </li>
            <xsl:if test="//resume">
              <li>
                <a href="#resume">{% trans "Résumé" %}</a>
              </li>
            </xsl:if>
            {% if content_access_granted and not only_display %}
            <xsl:if test="//section1/titre[not(@traitementparticulier='oui')]">
              <li class="article-toc--body">
                <ul class="unstyled">
                  <xsl:apply-templates select="corps/section1/titre[not(@traitementparticulier='oui')]" mode="toc-heading"/>
                </ul>
              </li>
            </xsl:if>
            {% endif %}
            {% if article.processing == 'M' and article.localidentifier and article.publication_allowed %}
            <li>
              <a href="#pdf-viewer" id="pdf-viewer-menu-link">{% trans 'Texte intégral (PDF)' %}</a>
              <a href="{% url 'public:journal:article_raw_pdf' article.issue.journal.code article.issue.volume_slug article.issue.localidentifier article.localidentifier %}{% if not article.issue.is_published %}?ticket={{ article.issue.prepublication_ticket }}{% endif %}" id="pdf-download-menu-link" target="_blank">{% trans 'Texte intégral (PDF)' %}</a>
            </li>
            {% endif %}
            <xsl:for-each select="partiesann[1]">
              {% if content_access_granted and not only_display %}
              <xsl:if test="grannexe">
                <li>
                  <a href="#grannexe">
                    <xsl:apply-templates select="grannexe" mode="toc-heading"/>
                  </a>
                </li>
              </xsl:if>
              <xsl:if test="merci">
                <li>
                  <a href="#merci">
                    <xsl:apply-templates select="merci" mode="toc-heading"/>
                  </a>
                </li>
              </xsl:if>
              <xsl:if test="grnotebio">
                <li>
                  <a href="#grnotebio">
                    <xsl:apply-templates select="grnotebio" mode="toc-heading"/>
                  </a>
                </li>
              </xsl:if>
              <xsl:if test="grnote">
                <li>
                  <a href="#grnote">
                    <xsl:apply-templates select="grnote" mode="toc-heading"/>
                  </a>
                </li>
              </xsl:if>
              {% endif %}
              {% if not is_of_type_roc %}
              <xsl:if test="grbiblio">
                <li>
                  <a href="#grbiblio">
                    <xsl:apply-templates select="grbiblio" mode="toc-heading"/>
                  </a>
                </li>
              </xsl:if>
              {% endif %}
            </xsl:for-each>
            {% if content_access_granted and not only_display %}
            <xsl:if test="//figure">
              <li>
                <a href="#figures">{% trans "Liste des figures" %}</a>
              </li>
            </xsl:if>
            <xsl:if test="//tableau">
              <li>
                <a href="#tableaux">{% trans "Liste des tableaux" %}</a>
              </li>
            </xsl:if>
            {% endif %}
          </ul>
          {% switch "maintenance" %}
          {% else %}
          {% if article.issue.is_published %}
          <!-- promotional campaign -->
          <aside class="campaign">
            <h2 class="sr-only">{% trans 'Érudit célèbre ses 20 ans!' %}</h2>
            <a href="{% url "public:20_years" %}" target="_blank" class="campaign-sidebar">
            <div id="campaign-sidebar" class="campaign-sidebar {% if LANGUAGE_CODE == 'en' %}en{% endif %}"></div>
            </a>
          </aside>
          {% endif %}
          {% endswitch %}
          {% if content_access_granted and subscription_type == 'individual' %}
          <div class="text-center">
            <p><em>{% trans "Vous êtes abonné à cette revue." %}</em></p>
          </div>
          {% endif %}
          {# We must not cache the subscription sponsor badge with the rest of this fragment #}
          {# because it has to vary based on the current user subscription. #}
          {% nocache %}
          {% include "public/partials/subscription_sponsor_badge.html" %}
          {% endnocache %}
        </nav>

        <!-- toolbox -->
        <aside class="pull-right toolbox-wrapper">
          <h2 class="sr-only">{% trans "Boîte à outils" %}</h2>
          {% spaceless %}
          <ul class="unstyled toolbox">
            <li class="hidden-md hidden-lg">
              <a class="scroll-top tool-btn tool-top" href="#top" title="{% trans 'Retourner en haut de la page' %}" aria-label="{% trans 'Retourner en haut de la page' %}">
                <i class="icon ion-ios-arrow-up toolbox-top"></i>
              </a>
            </li>
            {% switch "maintenance" %}
            {% else %}
            <li>
              <a class="tool-btn" id="tool-citation-save-{{ article.localidentifier }}" data-citation-save="#article-{{ article.localidentifier }}"{% if article.solr_id in request.saved_citations %} style="display:none;"{% endif %}>
                <i class="icon ion-ios-bookmark toolbox-save"></i>
                <span class="tools-label">{% trans "Sauvegarder" %}</span>
              </a>
              <a class="tool-btn saved" id="tool-citation-remove-{{ article.localidentifier }}" data-citation-remove="#article-{{ article.localidentifier }}"{% if not article.solr_id in request.saved_citations %} style="display:none;"{% endif %}>
                <i class="icon ion-ios-bookmark toolbox-save"></i>
                <span class="tools-label">{% trans "Supprimer" %}</span>
              </a>
            </li>
            {% endswitch %}
            {% if content_access_granted and pdf_exists %}
            <li>
              <a class="tool-btn tool-download" data-href="{% url 'public:journal:article_raw_pdf' article.issue.journal.code article.issue.volume_slug article.issue.localidentifier article.localidentifier %}{% if not article.issue.is_published %}?ticket={{ article.issue.prepublication_ticket }}{% endif %}">
                <span class="toolbox-pdf">PDF</span>
                <span class="tools-label">{% trans "Télécharger" %}</span>
              </a>
            </li>
            {% endif %}
            <li>
              <a class="tool-btn tool-cite" data-modal-id="#id_cite_modal_{{ article.localidentifier }}">
                <i class="icon ion-ios-quote toolbox-cite"></i>
                <span class="tools-label">{% trans "Citer cet article" %}</span>
              </a>
            </li>
            <li>
              <a class="tool-btn tool-share" data-cite="#id_cite_mla_{{ article.localidentifier }}">
                <xsl:attribute name="data-title">
                  {{ article|format_article_title|escape }}
                </xsl:attribute>
                <i class="icon ion-ios-share-alt toolbox-share"></i>
                <span class="tools-label">{% trans "Partager" %}</span>
              </a>
            </li>
          </ul>
          {% endspaceless %}
        </aside>
      </xsl:if>

      <div class="full-article {% if article.processing == 'C' %}col-md-7 col-md-offset-1{% else %} col-md-11 col-lg-8{% endif %}">
        {% if only_display != 'biblio' %}
        <!-- abstracts & keywords -->
        <xsl:if test="//resume | //grmotcle">
          <section id="resume" role="complementary" class="article-section grresume">
            <h2 class="sr-only">{% trans 'Résumés' %}</h2>
            <xsl:for-each select="//resume">
              <!-- if the abstract is the main one, make sure it appears first -->
              <xsl:sort select="number(contains(/article/@lang, @lang)) * -1"/>
              <xsl:call-template name="resume"/>
            </xsl:for-each>
            <!-- other keywords -->
            <xsl:for-each select="//grmotcle">
              <xsl:variable name="lang" select="@lang"/>
              <xsl:choose>
                <xsl:when test="//resume[@lang = $lang]">
                  <!-- do nothing -->
                </xsl:when>
                <xsl:otherwise>
                  <xsl:call-template name="motscles">
                    <xsl:with-param name="lang" select="@lang"/>
                  </xsl:call-template>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:for-each>
          </section>
        </xsl:if>
        {% endif %}

        {% if not article.publication_allowed %}
          {# Do nothong. #}
        {% elif content_access_granted and not only_display %}
          {% if article.processing == 'C' %}
          <!-- body -->
          <section id="corps" class="article-section corps" role="main">
            <h2 class="sr-only">{% trans "Corps de l’article" %}</h2>
            <xsl:apply-templates select="//corps"/>
          </section>
          {% elif article.localidentifier %}
          <object id="pdf-viewer" data="{% url 'public:journal:article_raw_pdf' article.issue.journal.code article.issue.volume_slug article.issue.localidentifier article.localidentifier %}?embed{% if not article.issue.is_published %}&amp;ticket={{ article.issue.prepublication_ticket }}{% endif %}" type="application/pdf" width="100%" height="700px"></object>
          <div id="pdf-download" class="text-center alert-warning">
            <p>{% trans 'Veuillez télécharger l’article en PDF pour le lire.' %}<br/><br/><a href="{% url 'public:journal:article_raw_pdf' article.issue.journal.code article.issue.volume_slug article.issue.localidentifier article.localidentifier %}{% if not article.issue.is_published %}?ticket={{ article.issue.prepublication_ticket }}{% endif %}" class="btn btn-secondary" target="_blank">{% trans 'Télécharger' %}</a></p>
          </div>
          {% endif %}
        {% elif article.abstracts or only_display == 'biblio' %}
          {# Do nothong. #}
        {% elif not article.abstracts and can_display_first_pdf_page %}
        <p>
          <object id="pdf-viewer" data="{% url 'public:journal:article_raw_pdf_firstpage' article.issue.journal.code article.issue.volume_slug article.issue.localidentifier article.localidentifier %}?embed{% if not article.issue.is_published %}&amp;ticket={{ article.issue.prepublication_ticket }}{% endif %}" type="application/pdf" width="100%" height="700px"></object>
        </p>
        {% elif article.issue.journal.is_scientific %}
          {{ article.html_body|safe|truncatewords_html:600 }}
        {% endif %}


        <!-- appendices -->
        <div class="row">
          <xsl:apply-templates select="partiesann[node()]"/>
        </div>

        <!-- lists of tables & figures -->
        {% if content_access_granted and not only_display %}
        <xsl:if test="//figure">
          <section id="figures" class="article-section figures" role="complementary">
            <h2>{% trans "Liste des figures" %}</h2>
            <xsl:for-each select="//grfigure | //figure[name(..) != 'grfigure']">
              <xsl:apply-templates select=".">
                <xsl:with-param name="mode" select="'liste'"/>
              </xsl:apply-templates>
            </xsl:for-each>
          </section>
        </xsl:if>

        <xsl:if test="//tableau">
          <section id="tableaux" class="article-section tableaux" role="complementary">
            <h2>{% trans "Liste des tableaux" %}</h2>
            <xsl:for-each select="//grtableau | //tableau[name(..) != 'grtableau']">
              <xsl:apply-templates select=".">
                <xsl:with-param name="mode" select="'liste'"/>
              </xsl:apply-templates>
            </xsl:for-each>
          </section>
        </xsl:if>
        {% endif %}

      </div>
    </div>

  </xsl:template>

  <!--=========== TEMPLATES ===========-->

  <!--**** HEADER ***-->
  <!-- identifiers -->
  <xsl:template match="idpublic[@scheme = 'doi']">
    <xsl:text>&#x0020;</xsl:text>
    <a href="{$doiStart}{.}" class="refbiblio-link {name()}" target="_blank">
      <xsl:if test="contains( . , '10.7202')">
        <img src="{% static 'svg/symbole-erudit.svg' %}" title="DOI Érudit" alt="Icône pour les DOIs Érudit" class="erudit-doi"/>
      </xsl:if>
      <xsl:value-of select="."/>
    </a>
  </xsl:template>

  <xsl:template match="idpublic[@scheme='uri']">
    <a href="{$uriStart}{.}" class="refbiblio-link {name()}" target="_blank">
      <xsl:text>URI:</xsl:text>
      <xsl:value-of select="."/>
    </a>
  </xsl:template>

  <!-- article type -->
  <xsl:template match="@typeart">
    <xsl:choose>
      <xsl:when test="$typeudoc = 'article'">{% trans "Un article" %}</xsl:when>
      <xsl:when test="$typeudoc = 'compterendu'">{% trans "Un compte rendu" %}</xsl:when>
      <xsl:when test="$typeudoc = 'note'">{% trans "Une note" %}</xsl:when>
      <xsl:otherwise>{% trans "Un document" %}</xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- issue-level section title / subhead -->
  <xsl:template match="liminaire/grtitre/surtitre | liminaire/grtitre/surtitreparal" mode="title">
    <span class="surtitre">
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!-- article title(s) -->
  <xsl:template match="article/liminaire/grtitre/titre | article/liminaire/grtitre/trefbiblio | article/liminaire/grtitre/sstitre" mode="title">
    <span class="{name()}">
      <xsl:choose>
        <xsl:when test="normalize-space() = '&#160;'">
          <xsl:text>{% trans "[Article sans titre]" %}</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="."/>
        </xsl:otherwise>
      </xsl:choose>
    </span>
  </xsl:template>

  <!-- alternate title(s) for multilingual articles -->
  <xsl:template match="article/liminaire/grtitre/titreparal | article/liminaire/grtitre/sstitreparal" mode="title">
    <span class="{name()}">
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!-- author(s) - person or organisation -->
  <xsl:template match="auteur[not(contribution[@typecontrib = 'trl'])]" mode="author">
    <li class="{name()} doc-head__author">
      <xsl:choose>
        <xsl:when test="nompers">
          <span class="nompers">
            <xsl:call-template name="element_nompers_affichage">
              <xsl:with-param name="nompers" select="nompers[1]"/>
              <xsl:with-param name="suffixes">false</xsl:with-param>
            </xsl:call-template>
            <xsl:if test="nompers[2][@typenompers = 'pseudonyme']">
              <xsl:text>, </xsl:text>
              <xsl:call-template name="element_nompers_affichage">
                <xsl:with-param name="nompers" select="nompers[2]"/>
                <xsl:with-param name="suffixes">false</xsl:with-param>
              </xsl:call-template>
            </xsl:if>
          </span>
        </xsl:when>
        <xsl:when test="nomorg/child::node()">
          <span class="nomorg">
            <xsl:call-template name="syntaxe_texte_affichage">
              <xsl:with-param name="texte" select="nomorg"/>
            </xsl:call-template>
            <xsl:if test="membre">
              <xsl:text>&#160;(</xsl:text>
              <xsl:for-each select="membre">
                <xsl:call-template name="element_nompers_affichage">
                  <xsl:with-param name="nompers" select="nompers"></xsl:with-param>
                  <xsl:with-param name="suffixes">false</xsl:with-param>
                </xsl:call-template>
                <xsl:if test="position() != last()"><xsl:text>, </xsl:text></xsl:if>
              </xsl:for-each>)
            </xsl:if>
          </span>
        </xsl:when>
      </xsl:choose>
      <xsl:choose>
        <xsl:when test="position() = last()-1">
          <xsl:text> {% trans 'et' %} </xsl:text>
        </xsl:when>
        <xsl:when test="position() != last()">
          <xsl:text>, </xsl:text>
        </xsl:when>
      </xsl:choose>
    </li>
  </xsl:template>

  <!-- author affiliations -->
  <xsl:template match="auteur" mode="affiliations">
    <xsl:for-each select=".">
      <li class="auteur-affiliation">
        <p>
          <xsl:apply-templates select="nompers | nomorg | contribution | affiliation/alinea | courriel | siteweb" mode="affiliations"/>
        </p>
      </li>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="nompers | nomorg | contribution | affiliation/alinea | courriel | siteweb" mode="affiliations">
    <xsl:for-each select=".">
      <xsl:choose>
        <xsl:when test="self::nompers">
          <strong>
            <xsl:call-template name="element_nompers_affichage">
              <xsl:with-param name="nompers" select="self::nompers[1]"/>
              <xsl:with-param name="suffixes">true</xsl:with-param>
            </xsl:call-template>
            <xsl:if test="self::nompers[2][@typenompers = 'pseudonyme']">
              <xsl:text>, </xsl:text>
              <xsl:call-template name="element_nompers_affichage">
                <xsl:with-param name="nompers" select="self::nompers[2]"/>
                <xsl:with-param name="suffixes">true</xsl:with-param>
              </xsl:call-template>
            </xsl:if>
          </strong>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    <xsl:if test="position() != last()"><br/></xsl:if>
  </xsl:template>

  <!-- admin notes: article history, editor's notes... -->
  <xsl:template match="article/liminaire/notegen | admin/histpapier">
    <div class="{name()}">
      <xsl:if test="titre">
        <h2>
          <xsl:apply-templates select="titre"/>
        </h2>
      </xsl:if>
      <xsl:apply-templates select="*[not(self::titre)]"/>
    </div>
  </xsl:template>

  <!-- admin notes: errata -->
  <xsl:template match="article/liminaire/erratum">
    <xsl:for-each select=".">
      <p class="{name()}">
        {% blocktrans %}
        --> Voir l’<a href="{@href}"><strong>erratum</strong></a> concernant cet article
        {% endblocktrans %}
      </p>
    </xsl:for-each>
  </xsl:template>

  <!-- issue volume / number -->
  <xsl:template match="admin/numero" mode="refpapier">
    <span class="volumaison">
      <xsl:for-each select="volume | nonumero[1] | pub/periode | pub/annee | pagination">
        <xsl:apply-templates select="."/>
        <xsl:choose>
          <xsl:when test="name(.) = name(following-sibling::*)">
            <xsl:text>–</xsl:text>
          </xsl:when>
          <xsl:when test="name(.) = 'periode' and name(following-sibling::*) = 'annee'">
            <xsl:text> </xsl:text>
          </xsl:when>
          <xsl:when test="position() != last()">
            <xsl:text>, </xsl:text>
          </xsl:when>
        </xsl:choose>
      </xsl:for-each>
    </span>
  </xsl:template>

  <xsl:template match="numero/volume">
    <span class="{name()}">
      <xsl:text{% blocktrans %}>Volume&#160;{% endblocktrans %}</xsl:text>
      <xsl:value-of select="."/>
    </span>
  </xsl:template>

  <xsl:template match="numero/nonumero[1]">
    <!-- template for first occurence of nonumero only; this allows the display of issues like Numéro 3-4 or Numéro 1-2-3 -->
    <span class="{name()}">
      <xsl:text>{% blocktrans %}Numéro&#160;{% endblocktrans %}</xsl:text>
      <!-- check if there are nonumero siblings -->
      <xsl:for-each select="parent::numero/nonumero">
        <xsl:value-of select="."/>
        <xsl:if test="position() != last()">
          <xsl:text>–</xsl:text>
        </xsl:if>
      </xsl:for-each>
    </span>
  </xsl:template>

  <xsl:template match="numero/periode | numero/annee">
    <span class="{name()}">
      <xsl:value-of select="."/>
    </span>
  </xsl:template>

  <xsl:template match="pagination">
    <xsl:if test="ppage[normalize-space()] | dpage[normalize-space()]">
      <xsl:text>, </xsl:text>
      <xsl:choose>
        <xsl:when test="ppage = dpage">p.&#160;<xsl:value-of select="ppage"/></xsl:when>
        <xsl:otherwise>{% trans 'p.' %}&#160;<xsl:value-of select="ppage"/>–<xsl:value-of select="dpage"/></xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <xsl:template match="ppage | dpage">
    <span class="{name()}">
      <xsl:value-of select="."/>
    </span>
  </xsl:template>

  <!-- themes -->
  <xsl:template match="admin/numero/grtheme/theme" mode="refpapier">
    <span class="{name()}">
      <br/>
      <strong>
        <a href="{% url 'public:journal:issue_detail' article.issue.journal.code article.issue.volume_slug article.issue.localidentifier %}"><xsl:apply-templates select="."/></a>
      </strong>
    </span>
  </xsl:template>

  <!-- copyright -->
  <xsl:template match="droitsauteur">
    <p class="{name()}">
      <small><xsl:apply-templates/></small>
    </p>
  </xsl:template>

  <xsl:template match="droitsauteur/nompers">
    <span class="nompers">
      <xsl:call-template name="element_nompers_affichage">
        <xsl:with-param name="nompers" select="."/>
      </xsl:call-template>
    </span>
  </xsl:template>

  <!--*** ARTICLE OUTLINE ***-->
  <xsl:template match="article/corps/section1/titre[not(@traitementparticulier='oui')]" mode="toc-heading">
    <li>
      <a href="#{../@id}">
        <xsl:apply-templates mode="toc-heading"/>
      </a>
    </li>
  </xsl:template>

  <xsl:template match="liensimple" mode="toc-heading">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="renvoi" mode="toc-heading">
    <!-- do not display anything -->
  </xsl:template>

  <xsl:template match="marquage" mode="toc-heading">
    <xsl:choose>
      <xsl:when test="@typemarq='gras'">
        <strong>
          <xsl:apply-templates select="node()[not(self::renvoi)]" mode="toc-heading"/>
        </strong>
      </xsl:when>
      <xsl:when test="@typemarq='italique'">
        <em>
          <xsl:apply-templates select="node()[not(self::renvoi)]" mode="toc-heading"/>
        </em>
      </xsl:when>
      <xsl:when test="@typemarq='taillep'">
        <small>
          <xsl:apply-templates select="node()[not(self::renvoi)]" mode="toc-heading"/>
        </small>
      </xsl:when>
      <xsl:otherwise>
        <span class="{@typemarq}">
          <xsl:apply-templates select="node()[not(self::renvoi)]" mode="toc-heading"/>
        </span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="exposant" mode="toc-heading">
    <xsl:element name="sup">
      <xsl:if test="@traitementparticulier = 'oui'">
        <xsl:attribute name="class">
          <xsl:text>{% trans "special" %}</xsl:text>
        </xsl:attribute>
      </xsl:if>
      <xsl:call-template name="syntaxe_texte_affichage">
        <xsl:with-param name="texte" select="."/>
      </xsl:call-template>
    </xsl:element>
  </xsl:template>

  <xsl:template match="indice" mode="toc-heading">
    <xsl:element name="sub">
      <xsl:if test="@traitementparticulier">
        <xsl:attribute name="class">
          <xsl:text>{% trans "special" %}</xsl:text>
        </xsl:attribute>
      </xsl:if>
      <xsl:call-template name="syntaxe_texte_affichage">
        <xsl:with-param name="texte" select="."/>
      </xsl:call-template>
    </xsl:element>
  </xsl:template>

  <xsl:template match="grannexe | grnotebio | grnote | merci | grbiblio"  mode="toc-heading">
    <xsl:if test="self::grannexe">
      <xsl:choose>
        <xsl:when test="titre and titre != null">
          <xsl:value-of select="titre"/>
        </xsl:when>
        <xsl:when test="count(annexe) = 1">{% trans "Annexe" %}</xsl:when>
        <xsl:otherwise>{% trans "Annexes" %}</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:if test="self::grnotebio">
      <xsl:choose>
        <xsl:when test="titre and titre != null">
          <xsl:value-of select="titre"/>
        </xsl:when>
        <xsl:when test="count(notebio) = 1">{% trans "Note biographique" %}</xsl:when>
        <xsl:otherwise>{% trans "Notes biographiques" %}</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:if test="self::grnote">
      <xsl:choose>
        <xsl:when test="titre and titre != null">
          <xsl:value-of select="titre"/>
        </xsl:when>
        <xsl:when test="count(note) = 1">{% trans "Note" %}</xsl:when>
        <xsl:otherwise>{% trans "Notes" %}</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:if test="self::merci">
      <xsl:choose>
        <xsl:when test="titre and titre != null" >
          <xsl:value-of select="titre"/>
        </xsl:when>
        <xsl:otherwise>{% trans "Remerciements" %}</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:if test="self::grbiblio">
      <xsl:choose>
        <xsl:when test="count(biblio) = 1">{% trans "Bibliographie" %}</xsl:when>
        <xsl:otherwise>{% trans "Bibliographies" %}</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>
  <!--*** BODY ***-->
  <xsl:template match="corps">
    <xsl:if test="@lang != preceding-sibling::*[@lang]">
      <hr />
    </xsl:if>
    <xsl:apply-templates select="*[not(self::texte)]"/>
  </xsl:template>

  <xsl:template match="section1">
    <section id="{@id}">
      <xsl:if test="titre">
        <xsl:element name="h2">
          <xsl:choose>
            <!-- When the title is empty, add the 'empty' class and don't bother applying templates. -->
            <xsl:when test="titre[normalize-space()] = '&#160;'">
              <xsl:attribute name="class">special empty</xsl:attribute>
            </xsl:when>
            <!-- When the title has special treatment, add the 'special' class and apply templates. -->
            <xsl:when test="titre/@traitementparticulier">
              <xsl:attribute name="class">special</xsl:attribute>
              <xsl:apply-templates select="titre"/>
            </xsl:when>
            <!-- Otherwise, apply templates. -->
            <xsl:otherwise>
              <xsl:apply-templates select="titre"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:element>
      </xsl:if>
      <xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
    </section>
  </xsl:template>
  <xsl:template match="section2">
    <section id="{@id}">
      <xsl:if test="titre">
        <xsl:element name="h3">
          <xsl:if test="titre/@traitementparticulier">
            <xsl:attribute name="class">{% trans "special" %}</xsl:attribute>
          </xsl:if>
          <xsl:apply-templates select="titre"/>
        </xsl:element>
      </xsl:if>
      <xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
    </section>
  </xsl:template>
  <xsl:template match="section3">
    <section id="{@id}">
      <xsl:if test="titre">
        <xsl:element name="h4">
          <xsl:if test="titre/@traitementparticulier">
            <xsl:attribute name="class">{% trans "special" %}</xsl:attribute>
          </xsl:if>
          <xsl:apply-templates select="titre"/>
        </xsl:element>
      </xsl:if>
      <xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
    </section>
  </xsl:template>
  <xsl:template match="section4">
    <section id="{@id}">
      <xsl:if test="titre">
        <xsl:element name="h5">
          <xsl:if test="titre/@traitementparticulier">
            <xsl:attribute name="class">{% trans "special" %}</xsl:attribute>
          </xsl:if>
          <xsl:apply-templates select="titre"/>
        </xsl:element>
      </xsl:if>
      <xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
    </section>
  </xsl:template>
  <xsl:template match="section5">
    <section id="{@id}">
      <xsl:if test="titre">
        <xsl:element name="h6">
          <xsl:if test="titre/@traitementparticulier">
            <xsl:attribute name="class">{% trans "special" %}</xsl:attribute>
          </xsl:if>
          <xsl:apply-templates select="titre"/>
        </xsl:element>
      </xsl:if>
      <xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
    </section>
  </xsl:template>
  <xsl:template match="section6">
    <section id="{@id}">
      <xsl:if test="titre">
        <xsl:element name="h6">
          <xsl:attribute name="class">h7</xsl:attribute>
          <xsl:if test="titre/@traitementparticulier">
            <xsl:attribute name="class">{% trans "special" %}</xsl:attribute>
          </xsl:if>
          <xsl:apply-templates select="titre"/>
        </xsl:element>
      </xsl:if>
      <xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
    </section>
  </xsl:template>
  <xsl:template match="para">
    <div class="{name()}" id="{@id}">
      <xsl:apply-templates select="no" mode="para"/>
      <xsl:apply-templates select="*[not(self::no)]"/>
    </div>
  </xsl:template>
  <xsl:template match="alinea">
    <p class="{name()}">
      <xsl:apply-templates/>
    </p>
  </xsl:template>
  <xsl:template match="no" mode="para"></xsl:template>
  <xsl:template match="section1/alinea|section2/alinea|section3/alinea|section4/alinea|section5/alinea|section6/alinea|grannexe/alinea"  priority="1">
    <p class="horspara">
      <xsl:apply-templates/>
    </p>
  </xsl:template>
  <xsl:template match="no">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="legende/titre | legende/sstitre">
    <p class="legende">
      <xsl:for-each select=".">
        <strong class="{name()}">
          <xsl:apply-templates/>
        </strong>
      </xsl:for-each>
    </p>
  </xsl:template>
  <xsl:template match="ligne">
    <xsl:apply-templates/>
    <br/>
  </xsl:template>
  <xsl:template match="titre">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="elemliste">
    <li>
      <xsl:apply-templates/>
    </li>
  </xsl:template>

  <!-- blockquotes, dedications, epigraphs, verbatims -->
  <xsl:template match="bloccitation | dedicace | epigraphe | verbatim">
    <blockquote class="{name()} {@typeverb}">
      <xsl:choose>
        <xsl:when test="@typeverb = 'poeme'">
          <xsl:apply-templates mode="poeme"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates/>
        </xsl:otherwise>
      </xsl:choose>
    </blockquote>
  </xsl:template>

  <xsl:template match="bloccitation/source | dedicace/source | epigraphe/source | verbatim/source">
    <cite class="source">
      <xsl:apply-templates/>
    </cite>
  </xsl:template>

  <xsl:template match="bloc">
    <p class="bloc {@alignh}">
      <xsl:apply-templates/>
    </p>
  </xsl:template>

  <xsl:template match="bloc/ligne">
    <xsl:apply-templates/>
    <br/>
  </xsl:template>

  <xsl:template match="bloc" mode="poeme">
    <div class="bloc"><xsl:apply-templates mode="poeme"/></div>
  </xsl:template>

  <xsl:template match="bloc/ligne" mode="poeme">
    <p class="ligne"><xsl:apply-templates/></p>
  </xsl:template>

  <!-- groups of figures & tables -->
  <xsl:template match="grfigure | grtableau">
    <xsl:param name="mode"/>
    <xsl:variable name="id">
      <xsl:choose>
        <xsl:when test="$mode = 'liste'">
          <xsl:value-of select="concat('li', @id)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="@id"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <div class="{name()}" id="{$id}">
      <div class="grfigure-caption">
        <xsl:if test="$mode = 'liste'">
          <p class="allertexte"><a href="#{@id}">|^</a></p>
        </xsl:if>
        <p class="no"><xsl:apply-templates select="no"/></p>
        <div class="legende"><xsl:apply-templates select="legende/titre | legende/sstitre"/></div>
      </div>
      <xsl:apply-templates select="tableau | figure">
        <xsl:with-param name="mode" select="$mode"/>
      </xsl:apply-templates>
      <div class="grfigure-legende">
        <xsl:apply-templates select="legende/alinea | legende/bloccitation | legende/listenonord | legende/listeord | legende/listerelation | legende/objetmedia | legende/refbiblio | legende/tabtexte | legende/verbatim"/>
      </div>
      <xsl:if test="not($mode)">
        <p class="voirliste">
          <a href="#li{@id}">{% blocktrans %}-> Voir la liste des <xsl:if test="self::grfigure">figures</xsl:if><xsl:if test="self::grtableau">tableaux</xsl:if>{% endblocktrans %}</a>
        </p>
      </xsl:if>
    </div>
  </xsl:template>

  <!-- figures & tables -->
  <xsl:template match="tableau | figure">
    <xsl:param name="mode"/>
    <xsl:variable name="id">
      <xsl:choose>
        <xsl:when test="$mode = 'liste'">
          <xsl:value-of select="concat('li', @id)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="@id"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <figure class="{name()}" id="{$id}">
      <figcaption>
        <xsl:if test="name(..) != 'grfigure' and name(..) != 'grtableau'">
          <xsl:if test="$mode = 'liste'">
            <p class="allertexte"><a href="#{@id}">|^</a></p>
          </xsl:if>
        </xsl:if>
        <xsl:if test="no">
          <p class="no"><xsl:apply-templates select="no"/></p>
        </xsl:if>
        <xsl:apply-templates select="legende/titre | legende/sstitre"/>
      </figcaption>
      <div class="figure-wrapper">
        <div class="figure-object">
          <xsl:apply-templates select="tabtexte | objetmedia"/>
        </div>
        <div class="figure-legende-notes-source">
          <xsl:if test="legende/alinea | legende/bloccitation | legende/listenonord | legende/listeord | legende/listerelation | legende/objetmedia | legende/refbiblio | legende/tabtexte | legende/verbatim">
            <div class="figure-legende">
              <xsl:apply-templates select="legende/alinea | legende/bloccitation | legende/listenonord | legende/listeord | legende/listerelation | legende/objetmedia | legende/refbiblio | legende/tabtexte | legende/verbatim"/>
            </div>
          </xsl:if>
          <xsl:apply-templates select="notefig | notetabl"/>
          <xsl:apply-templates select="source | ancestor::grfigure/source"/>
        </div>
      </div>
      <xsl:if test="not($mode) and name(..) != 'grfigure' and name(..) != 'grtableau'">
        <p class="voirliste">
          <a href="#li{@id}">{% blocktrans %}-> Voir la liste des <xsl:if test="self::figure">figures</xsl:if><xsl:if test="self::tableau">tableaux</xsl:if>{% endblocktrans %}</a>
        </p>
      </xsl:if>
    </figure>
  </xsl:template>

  <!-- media tables -->
  <xsl:template match="figure/objetmedia|tableau/objetmedia">
    <xsl:variable name="imgPlGrId" select="concat('plgr-', image/@id)"/>
    <xsl:variable name="imgPlGr" select="$vars[@n = $imgPlGrId]/@value" />
    <a href="{{ media_url_prefix }}{$imgPlGr}" class="lightbox {name()}"  title="{normalize-space(../legende/titre)}">
      <img src="{{ media_url_prefix }}{$imgPlGr}" alt="{normalize-space(../legende/titre)}" class="img-responsive"/>
    </a>
  </xsl:template>

  <!-- text tables -->
  <xsl:template match="tabtexte">
    <xsl:variable name="valeurID" select="@id"/>
    <xsl:variable name="type" select="@type"/>
    <xsl:element name="table">
      <xsl:attribute name="id">
        <xsl:value-of select="$valeurID"/>
      </xsl:attribute>
      <xsl:attribute name="lang">
        <xsl:value-of select="@lang"/>
      </xsl:attribute>
      <xsl:attribute name="class">
        <xsl:value-of select="concat( 'tabtexte', $type )"/>
        <xsl:choose>
          <xsl:when test="$type = '1' or $type = '2'"><xsl:text> frame-hsides</xsl:text></xsl:when>
          <xsl:when test="$type = '3' or $type = '4'"><xsl:text> frame-box</xsl:text></xsl:when>
          <xsl:otherwise><xsl:text> frame-void</xsl:text></xsl:otherwise>
        </xsl:choose>
        <xsl:choose>
          <xsl:when test="$type = '5'"><xsl:text> rules-none</xsl:text></xsl:when>
          <xsl:otherwise><xsl:text> rules-groups</xsl:text></xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template name="tradAttr">
    <xsl:param name="noeudTab"/>
    <xsl:variable name="id" select="$noeudTab/@id"/>
    <xsl:variable name="identete" select="$noeudTab/@identete"/>
    <xsl:variable name="nbcol" select="$noeudTab/@nbcol"/>
    <xsl:variable name="nbligne" select="$noeudTab/@nbligne"/>
    <xsl:variable name="portee" select="$noeudTab/@portee"/>
    <xsl:variable name="alignh" select="$noeudTab/@alignh"/>
    <xsl:variable name="carac" select="$noeudTab/@carac"/>
    <xsl:variable name="alignv" select="$noeudTab/@alignv"/>

    <xsl:if test="$id">
      <xsl:attribute name="id"><xsl:value-of select="$id"/></xsl:attribute>
    </xsl:if>
    <xsl:if test="$identete">
      <xsl:attribute name="headers"><xsl:value-of select="$identete"/></xsl:attribute>
    </xsl:if>
    <xsl:if test="$alignh | $alignv">
      <xsl:attribute name="class">
        <xsl:if test="$alignh">
          <xsl:text>align </xsl:text>
          <xsl:choose>
            <xsl:when test="$alignh = 'gauche'">
              <xsl:text>align-left</xsl:text>
            </xsl:when>
            <xsl:when test="$alignh = 'centre'">
              <xsl:text>align-center</xsl:text>
            </xsl:when>
            <xsl:when test="$alignh = 'droite'">
              <xsl:text>align-right</xsl:text>
            </xsl:when>
            <xsl:when test="$alignh = 'justifie'">
              <xsl:text>align-justify</xsl:text>
            </xsl:when>
            <xsl:when test="$alignh = 'carac'">
              <xsl:text>align-char</xsl:text>
            </xsl:when>
          </xsl:choose>
        </xsl:if>
        <xsl:if test="$alignv">
          <xsl:text>valign </xsl:text>
          <xsl:choose>
            <xsl:when test="$alignv = 'haut'">
              <xsl:text>valign-top</xsl:text>
            </xsl:when>
            <xsl:when test="$alignv = 'centre'">
              <xsl:text>valign-middle</xsl:text>
            </xsl:when>
            <xsl:when test="$alignv = 'bas'">
              <xsl:text>valign-bottom</xsl:text>
            </xsl:when>
            <xsl:when test="$alignv = 'lignebase'">
              <xsl:text>valign-baseline</xsl:text>
            </xsl:when>
          </xsl:choose>
        </xsl:if>
      </xsl:attribute>
    </xsl:if>
    <xsl:if test="$nbcol">
      <xsl:choose>
        <xsl:when test="$noeudTab/self::tabgrcol">
          <xsl:attribute name="span">
            <xsl:value-of select="$nbcol"/>
          </xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="span">
            <xsl:value-of select="$nbcol"/>
          </xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:if test="$nbligne">
      <xsl:attribute name="rowspan"><xsl:value-of select="$nbligne"/></xsl:attribute>
    </xsl:if>
    <xsl:if test="$portee">
      <xsl:choose>
        <xsl:when test="$portee = 'ligne'">
          <xsl:attribute name="scope"><xsl:text>row</xsl:text></xsl:attribute>
        </xsl:when>
        <xsl:when test="$portee = 'colonne'">
          <xsl:attribute name="scope"><xsl:text>col</xsl:text></xsl:attribute>
        </xsl:when>
        <xsl:when test="$portee = 'grligne'">
          <xsl:attribute name="scope"><xsl:text>rowgroup</xsl:text></xsl:attribute>
        </xsl:when>
        <xsl:when test="$portee = 'grcolonne'">
          <xsl:attribute name="scope"><xsl:text>colgroup</xsl:text></xsl:attribute>
        </xsl:when>
      </xsl:choose>
    </xsl:if>
    <xsl:if test="$carac">
      <xsl:attribute name="char"><xsl:value-of select="$carac"/></xsl:attribute>
    </xsl:if>
  </xsl:template>

  <xsl:template match="tabcol">
    <xsl:element name="col">
      <xsl:call-template name="tradAttr">
        <xsl:with-param name="noeudTab" select="."/>
      </xsl:call-template>
    </xsl:element>
  </xsl:template>

  <xsl:template match="tabgrcol">
    <xsl:element name="colgroup">
      <xsl:call-template name="tradAttr">
        <xsl:with-param name="noeudTab" select="."/>
      </xsl:call-template>
      <xsl:apply-templates/> <!-- tabcol* -->
    </xsl:element>
  </xsl:template>

  <xsl:template match="tabentete">
    <xsl:element name="thead">
      <xsl:call-template name="tradAttr">
        <xsl:with-param name="noeudTab" select="."/>
      </xsl:call-template>
      <xsl:apply-templates/> <!-- tabligne+ -->
    </xsl:element>
  </xsl:template>

  <xsl:template match="tabligne">
    <xsl:element name="tr">
      <xsl:call-template name="tradAttr">
        <xsl:with-param name="noeudTab" select="."/>
      </xsl:call-template>
      <xsl:apply-templates/> <!-- (tabcellulee | tabcelluled)+ -->
    </xsl:element>
  </xsl:template>

  <xsl:template match="tabcelluled">
    <xsl:element name="td">
      <xsl:call-template name="tradAttr">
        <xsl:with-param name="noeudTab" select="."/>
      </xsl:call-template>
      <xsl:apply-templates/> <!-- blocimbrique+ -->
    </xsl:element>
  </xsl:template>

  <xsl:template match="tabcellulee">
    <xsl:element name="th">
      <xsl:call-template name="tradAttr">
        <xsl:with-param name="noeudTab" select="."/>
      </xsl:call-template>
      <xsl:apply-templates/> <!-- blocimbrique+ -->
    </xsl:element>
  </xsl:template>

  <xsl:template match="tabpied">
    <xsl:element name="tfoot">
      <xsl:call-template name="tradAttr">
        <xsl:with-param name="noeudTab" select="."/>
      </xsl:call-template>
      <xsl:apply-templates/> <!-- tabligne+ -->
    </xsl:element>
  </xsl:template>

  <xsl:template match="tabgrligne">
    <xsl:element name="tbody">
      <xsl:call-template name="tradAttr">
        <xsl:with-param name="noeudTab" select="."/>
      </xsl:call-template>
      <xsl:apply-templates/> <!-- tabligne+ -->
    </xsl:element>
  </xsl:template>

  <!-- equations, examples & insets/boxed text -->
  <xsl:template match="grencadre|grequation|grexemple">
    <aside class="{name()}">
      <h1><strong><xsl:apply-templates select="no"/><xsl:apply-templates select="legende/titre"/></strong></h1>
      <xsl:apply-templates select="*[not(self::no)][not(self::legende)][not(self::titreparal)]"/>
    </aside>
  </xsl:template>

  <xsl:template match="encadre|exemple">
    <aside class="{name()}">
      <xsl:if test="legende or no">
        <h1>
          <strong>
            <xsl:apply-templates select="no"/><xsl:if test="legende and no"><span>. </span></xsl:if>
            <xsl:apply-templates select="legende"/>
          </strong>
        </h1>
      </xsl:if>
      <xsl:for-each select="node()[name() != '' and name() != 'no' and name() != 'legende']">
        <xsl:apply-templates select="."/>
      </xsl:for-each>
    </aside>
  </xsl:template>

  <xsl:template match="encadre/legende/titre|exemple/legende/titre|encadre/no|exemple/no">
    <xsl:apply-templates/>
  </xsl:template>

  <!-- notes within equations, examples and insets -->
  <xsl:template match="noteenc|noteeq|noteex">
    <xsl:call-template name="noteillustrationtype">
      <xsl:with-param name="noteIllustration" select="."/>
    </xsl:call-template>
  </xsl:template>
  <xsl:template match="equation">
    <xsl:variable name="valeurID" select="@id"/>
    <aside class="equation">
      <!-- Les numéros -->
      <xsl:for-each select="no">
        <span class="no">
          <xsl:call-template name="syntaxe_texte_affichage">
            <xsl:with-param name="texte" select="."/>
          </xsl:call-template>
        </span>
      </xsl:for-each>
      <!-- L'équation proprement dite -->
      <xsl:for-each        select="node()[ name() = 'alinea' or name() = 'bloccitation' or name() = 'listenonord' or name() = 'listeord' or name() = 'listerelation' or        name() = 'objetmedia' or        name() = 'refbiblio' or        name() = 'verbatim']">
        <xsl:apply-templates select="."/>
      </xsl:for-each>
      <!-- Les légendes -->
      <xsl:if test="legende">
        <div class="legende">
          <xsl:for-each select="legende">
            <xsl:apply-templates/>
          </xsl:for-each>
        </div>
      </xsl:if>
      <xsl:for-each select="node()[name() = 'noteeq' or name() = 'source']">
        <xsl:apply-templates select="."/>
      </xsl:for-each>
    </aside>
  </xsl:template>

  <!-- grobjet & objet -->
  <xsl:template match="grobjet">
    <div class="media media-group">
      <xsl:apply-templates/>
    </div>
  </xsl:template>
  <xsl:template match="objet">
    <div class="media">
      <p><xsl:apply-templates select="no"/></p>
      <xsl:apply-templates select="legende/titre"/>
      <xsl:apply-templates select="legende/sstitre"/>
      <xsl:apply-templates select="objetmedia/audio | objetmedia/video"/>
      <xsl:apply-templates select="legende/node()[not(self::titre)][not(self::sstitre)]"/>
    </div>
  </xsl:template>

  <!-- media objects -->
  <xsl:template match="objetmedia/audio">
    <xsl:variable name="nomAud" select="@*[local-name()='href']"/>
    <audio class="media-object" id="{@id}" preload="metadata" controls="controls">
      <source src="http://erudit.org/media/{$titreAbrege}/{$iderudit}/{$nomAud}" type="{@typemime}" />
      <p><em>{% trans 'Votre navigateur ne supporte pas les fichiers audio. Veuillez le mettre à jour.' %}</em></p>
    </audio>
  </xsl:template>

  <xsl:template match="objetmedia/video">
    <xsl:variable name="videohref" select="@*[local-name()='href']"/>
    <xsl:variable name="nomVid" select="substring-before($videohref, '.')"/>
    <div class="embed-responsive embed-responsive-4by3">
      <video class="embed-responsive-item" id="{@id}" preload="metadata" controls="controls">
        <source src="http://erudit.org/media/{$titreAbrege}/{$iderudit}/{$nomVid}.mp4" type="video/mp4" />
        <p><em>{% trans 'Votre navigateur ne supporte pas les fichiers vidéo. Veuillez le mettre à jour.' %}</em></p>
      </video>
    </div>
  </xsl:template>

  <xsl:template match="objetmedia/image">
    <xsl:variable name="nomImg" select="@href" xmlns:xlink="http://www.w3.org/1999/xlink" />
    <xsl:variable name="titreImg" select="@title" xmlns:xlink="http://www.w3.org/1999/xlink" />
    <xsl:element name="img">
      <xsl:attribute name="src">
        <xsl:if test="not(starts-with($nomImg , 'http'))">{{ media_url_prefix }}</xsl:if><xsl:value-of select="$nomImg"/>
      </xsl:attribute>
      <xsl:attribute name="id">
        <xsl:value-of select="@id"/>
      </xsl:attribute>
      <xsl:attribute name="alt">
        <xsl:value-of select="@typeimage"/>
        <xsl:text>: </xsl:text>
        <xsl:value-of select="desc | $titreImg"/>
      </xsl:attribute>
    </xsl:element>
  </xsl:template>

  <xsl:template match="objetmedia/texte">
  </xsl:template>

  <!-- lists -->
  <xsl:template match="listenonord">
    <xsl:variable name="signe" select="@signe"/>
    <xsl:choose>
      <xsl:when test="@nbcol">
        <!-- listenonord multi-colonnes -->
        <xsl:variable name="elemlistes" select="elemliste"/>
        <xsl:variable name="nbElems" select="count($elemlistes)"/>
        <xsl:variable name="nbCols" select="@nbcol"/>
        <xsl:variable name="divClass" select="concat('nbcol', $nbCols)"/>
        <xsl:variable name="quotient" select="floor($nbElems div $nbCols)"/>
        <xsl:variable name="reste" select="$nbElems mod $nbCols"/>
        <!-- maximum 5 colonnes -->
        <div class="multicolonne">
          <xsl:variable name="arret1" select="$quotient + number($reste &gt; 0)"/>
          <div class="{$divClass}">
            <ul class="{$signe}">
              <xsl:for-each select="elemliste[position() &gt; 0 and position() &lt;= $arret1]">
                <xsl:apply-templates select="."/>
              </xsl:for-each>
            </ul>
          </div>
          <xsl:if test="$nbCols &gt;= 2">
            <xsl:variable name="arret2" select="$arret1 + $quotient + number($reste &gt; 1)"/>
            <div class="{$divClass}">
              <ul class="{$signe}">
                <xsl:for-each select="elemliste[position() &gt; $arret1 and position() &lt;= $arret2]">
                  <xsl:apply-templates select="."/>
                </xsl:for-each>
              </ul>
            </div>
            <xsl:if test="$nbCols &gt;= 3">
              <xsl:variable name="arret3" select="$arret2 + $quotient + number($reste &gt; 2)"/>
              <div class="{$divClass}">
                <ul class="{$signe}">
                  <xsl:for-each select="elemliste[position() &gt; $arret2 and position() &lt;= $arret3]">
                    <xsl:apply-templates select="."/>
                  </xsl:for-each>
                </ul>
              </div>
              <xsl:if test="$nbCols &gt;= 4">
                <xsl:variable name="arret4" select="$arret3 + $quotient + number($reste &gt; 3)"/>
                <div class="{$divClass}">
                  <ul class="{$signe}">
                    <xsl:for-each select="elemliste[position() &gt; $arret3 and position() &lt;= $arret4]">
                      <xsl:apply-templates select="."/>
                    </xsl:for-each>
                  </ul>
                </div>
                <xsl:if test="$nbCols &gt;= 5">
                  <xsl:variable name="arret5" select="$arret4 + $quotient + number($reste &gt; 4)"/>
                  <div class="{$divClass}">
                    <ul class="{$signe}">
                      <xsl:for-each select="elemliste[position() &gt; $arret4 and position() &lt;= $arret5]">
                        <xsl:apply-templates select="."/>
                      </xsl:for-each>
                    </ul>
                  </div>
                </xsl:if>
              </xsl:if>
            </xsl:if>
          </xsl:if>
        </div>
      </xsl:when>
      <xsl:otherwise>
        <!-- listenonord 1 colonne -->
        <ul class="{@signe}">
          <xsl:apply-templates/>
        </ul>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="listeord">
    <xsl:variable name="numeration" select="@numeration"/>
    <xsl:variable name="start">
      <xsl:choose>
        <xsl:when test="@compteur">
          <xsl:value-of select="@compteur"/>
        </xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="@nbcol">
        <!-- listeord multi-colonnes -->
        <xsl:variable name="elemlistes" select="elemliste"/>
        <xsl:variable name="nbElems" select="count($elemlistes)"/>
        <xsl:variable name="nbCols" select="@nbcol"/>
        <xsl:variable name="divClass" select="concat('nbcol', $nbCols)"/>
        <xsl:variable name="quotient" select="floor($nbElems div $nbCols)"/>
        <xsl:variable name="reste" select="$nbElems mod $nbCols"/>
        <!-- maximum 5 colonnes -->
        <div class="multicolonne">
          <xsl:variable name="arret1" select="$quotient + number($reste &gt; 0)"/>
          <div class="{$divClass}">
            <ol class="{$numeration}" start="{$start}">
              <xsl:for-each select="elemliste[position() &gt; 0 and position() &lt;= $arret1]">
                <xsl:apply-templates select="."/>
              </xsl:for-each>
            </ol>
          </div>
          <xsl:if test="$nbCols &gt;= 2">
            <xsl:variable name="arret2" select="$arret1 + $quotient + number($reste &gt; 1)"/>
            <div class="{$divClass}">
              <ol class="{$numeration}" start="{$start + $arret1}">
                <xsl:for-each select="elemliste[position() &gt; $arret1 and position() &lt;= $arret2]">
                  <xsl:apply-templates select="."/>
                </xsl:for-each>
              </ol>
            </div>
            <xsl:if test="$nbCols &gt;= 3">
              <xsl:variable name="arret3" select="$arret2 + $quotient + number($reste &gt; 2)"/>
              <div class="{$divClass}">
                <ol class="$numeration" start="{$start + $arret2}">
                  <xsl:for-each select="elemliste[position() &gt; $arret2 and position() &lt;= $arret3]">
                    <xsl:apply-templates select="."/>
                  </xsl:for-each>
                </ol>
              </div>
              <xsl:if test="$nbCols &gt;= 4">
                <xsl:variable name="arret4" select="$arret3 + $quotient + number($reste &gt; 3)"/>
                <div class="{$divClass}">
                  <ol class="$numeration" start="{$start + $arret3}">
                    <xsl:for-each select="elemliste[position() &gt; $arret3 and position() &lt;= $arret4]">
                      <xsl:apply-templates select="."/>
                    </xsl:for-each>
                  </ol>
                </div>
                <xsl:if test="$nbCols &gt;= 5">
                  <xsl:variable name="arret5" select="$arret4 + $quotient + number($reste &gt; 4)"/>
                  <div class="{$divClass}">
                    <ol class="$numeration" start="{$start + $arret4}">
                      <xsl:for-each select="elemliste[position() &gt; $arret4 and position() &lt;= $arret5]">
                        <xsl:apply-templates select="."/>
                      </xsl:for-each>
                    </ol>
                  </div>
                </xsl:if>
              </xsl:if>
            </xsl:if>
          </xsl:if>
        </div>
      </xsl:when>
      <xsl:otherwise>
        <!-- listeord 1 colonne -->
        <xsl:element name="ol">
          <xsl:attribute name="class">
            <xsl:value-of select="@numeration"/>
          </xsl:attribute>
          <xsl:if test="@compteur">
            <xsl:attribute name="start">
              <xsl:value-of select="$start"/>
            </xsl:attribute>
          </xsl:if>
          <xsl:apply-templates/>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="listerelation">
    <!-- Syntaxe (#PCDATA | %texte;)* mode affichage -->
    <xsl:variable name="type" select="@type"/>
    <xsl:variable name="numeration" select="@numeration"/>
    <xsl:variable name="tableClass" select="concat( 'listerelation type', $type )"/>
    <xsl:variable name="nos" select="no"/>
    <xsl:variable name="lrsources" select="lrsource"/>
    <xsl:variable name="lrcibles" select="lrcible"/>
    <xsl:variable name="symbole" select="@symbole"/>
    <xsl:choose>
      <xsl:when test="@nbcol">
        <!-- listerelation colonnes multiples (2) -->
        <xsl:variable name="nbCols" select="@nbcol"/>
        <xsl:variable name="divClass" select="concat('nbcol', $nbCols)"/>
        <xsl:variable name="nbElems" select="count($lrsources)"/>
        <xsl:variable name="quotient" select="floor($nbElems div $nbCols)"/>
        <xsl:variable name="reste" select="$nbElems mod $nbCols"/>
        <xsl:variable name="arret1" select="$quotient + number( $reste &gt; 0 )"/>
        <div class="multicolonne">
          <xsl:choose>
            <xsl:when test="$type &lt; 4">
              <div class="{$divClass}">
                <table class="{$tableClass}">
                  <xsl:for-each select="$lrsources[ position() &lt;= $arret1]">
                    <xsl:variable name="seq" select="position()"/>
                    <tr>
                      <xsl:if test="$nos">
                        <td class="lrno">
                          <p>
                            <xsl:call-template name="syntaxe_texte_affichage">
                              <xsl:with-param name="texte" select="$nos[$seq]"/>
                            </xsl:call-template>
                          </p>
                        </td>
                      </xsl:if>
                      <td class="lrsource">
                        <xsl:apply-templates/>
                      </td>
                      <xsl:if test="$symbole != ''">
                        <td class="centre_symbole">
                          <span>
                            <xsl:value-of select="$symbole"/>
                          </span>
                        </td>
                      </xsl:if>
                      <td class="lrcible">
                        <xsl:apply-templates select="$lrcibles[$seq]"/>
                      </td>
                    </tr>
                  </xsl:for-each>
                </table>
              </div>
              <xsl:if test="$arret1 &lt; $nbElems">
                <div class="$divClass">
                  <table class="{$tableClass}">
                    <xsl:for-each select="$lrsources[ (position() &gt; $arret1) and (position() &lt;= $nbElems) ]">
                      <xsl:variable name="seq" select="position()"/>
                      <tr>
                        <xsl:if test="$nos">
                          <td class="lrno">
                            <p>
                              <xsl:call-template name="syntaxe_texte_affichage">
                                <xsl:with-param name="texte" select="$nos[$arret1 + $seq]"/>
                              </xsl:call-template>
                            </p>
                          </td>
                        </xsl:if>
                        <td class="lrsource">
                          <xsl:apply-templates/>
                        </td>
                        <xsl:if test="$symbole != ''">
                          <td class="centre_symbole">
                            <span>
                              <xsl:value-of select="$symbole"/>
                            </span>
                          </td>
                        </xsl:if>
                        <td class="lrcible">
                          <xsl:apply-templates select="$lrcibles[$arret1 + $seq]"/>
                        </td>
                      </tr>
                    </xsl:for-each>
                  </table>
                </div>
              </xsl:if>
            </xsl:when>
            <xsl:otherwise>
              <div class="{$divClass}">
                <table class="{$tableClass}">
                  <xsl:for-each select="$lrsources[ position() &lt;= $arret1]">
                    <xsl:variable name="seq" select="position()"/>
                    <tr>
                      <xsl:if test="$nos">
                        <td class="lrno" rowspan="2">
                          <p>
                            <xsl:call-template name="syntaxe_texte_affichage">
                              <xsl:with-param name="texte" select="$nos[$seq]"/>
                            </xsl:call-template>
                          </p>
                        </td>
                      </xsl:if>
                      <td class="lrsource">
                        <xsl:apply-templates/>
                      </td>
                    </tr>
                    <tr>
                      <td class="lrcible">
                        <xsl:apply-templates select="$lrcibles[$seq]"/>
                      </td>
                    </tr>
                  </xsl:for-each>
                </table>
              </div>
              <xsl:if test="$arret1 &lt; $nbElems">
                <div class="{$divClass}">
                  <table class="{$tableClass}">
                    <xsl:for-each select="$lrsources[ (position() &gt; $arret1) and (position() &lt;= $nbElems) ]">
                      <xsl:variable name="seq" select="position()"/>
                      <tr>
                        <xsl:if test="$nos">
                          <td class="lrno" rowspan="2">
                            <p>
                              <xsl:call-template name="syntaxe_texte_affichage">
                                <xsl:with-param name="texte" select="$nos[$arret1 + $seq]"/>
                              </xsl:call-template>
                            </p>
                          </td>
                        </xsl:if>
                        <td class="lrsource">
                          <xsl:apply-templates/>
                        </td>
                      </tr>
                      <tr>
                        <td class="lrcible">
                          <xsl:apply-templates select="$lrcibles[$arret1 + $seq]"/>
                        </td>
                      </tr>
                    </xsl:for-each>
                  </table>
                </div>
              </xsl:if>
            </xsl:otherwise>
          </xsl:choose>
        </div>
      </xsl:when>
      <xsl:otherwise>
        <!-- listerelation colonne unique -->
        <table class="{$tableClass}">
          <xsl:if test="lrsourcee or lrciblee">
            <tr>
              <xsl:if test="$numeration != '' ">
                <td/>
              </xsl:if>
              <xsl:for-each select="lrsourcee">
                <th>
                  <xsl:apply-templates/>
                </th>
              </xsl:for-each>
              <xsl:for-each select="lrciblee">
                <th>
                  <xsl:apply-templates/>
                </th>
              </xsl:for-each>
            </tr>
          </xsl:if>
          <xsl:choose>
            <xsl:when test="$type &lt; 4">
              <!-- listerelation colonne unique type 1, 2 ou 3 -->
              <xsl:choose>
                <!-- nouveau cas -->
                <xsl:when test="elemrelation">
                  <xsl:for-each select="elemrelation">
                    <xsl:variable name="seq" select="position()"/>
                    <tr>
                      <xsl:if test="$numeration">
                        <td class="numerotation">
                          <p>
                            <xsl:choose>
                              <xsl:when test="$numeration ='decimal'">
                                <xsl:number value="$seq" format="1."/>
                              </xsl:when>
                              <xsl:when test="$numeration ='lettremaj'">
                                <xsl:number value="$seq" format="A."/>
                              </xsl:when>
                              <xsl:when test="$numeration ='lettremin'">
                                <xsl:number value="$seq" format="a."/>
                              </xsl:when>
                              <xsl:when test="$numeration ='romainmaj'">
                                <xsl:number value="$seq" format="I."/>
                              </xsl:when>
                              <xsl:when test="$numeration ='romainmin'">
                                <xsl:number value="$seq" format="i."/>
                              </xsl:when>
                            </xsl:choose>
                          </p>
                        </td>
                      </xsl:if>
                      <xsl:if test="$nos">
                        <td class="lrno">
                          <p>
                            <xsl:call-template name="syntaxe_texte_affichage">
                              <xsl:with-param name="texte" select="$nos[$seq]"/>
                            </xsl:call-template>
                          </p>
                        </td>
                      </xsl:if>
                      <xsl:for-each select="lrsource">
                        <td class="lrsource">
                          <xsl:apply-templates/>
                        </td>
                        <xsl:if test="$symbole ">
                          <td class="centre_symbole">
                            <span>
                              <xsl:value-of select="$symbole"/>
                            </span>
                          </td>
                        </xsl:if>
                      </xsl:for-each>
                      <xsl:for-each select="lrcible">
                        <td class="lrcible">
                          <xsl:apply-templates/>
                        </td>
                      </xsl:for-each>
                    </tr>
                  </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
                  <!-- ancien cas -->
                  <xsl:for-each select="$lrsources">
                    <xsl:variable name="seq" select="position()"/>
                    <tr>
                      <xsl:if test="$nos">
                        <td class="lrno">
                          <p>
                            <xsl:call-template name="syntaxe_texte_affichage">
                              <xsl:with-param name="texte" select="$nos[$seq]"/>
                            </xsl:call-template>
                          </p>
                        </td>
                      </xsl:if>
                      <td class="lrsource">
                        <xsl:apply-templates/>
                      </td>
                      <xsl:if test="$symbole ">
                        <td class="centre_symbole">
                          <span>
                            <xsl:value-of select="$symbole"/>
                          </span>
                        </td>
                      </xsl:if>
                      <td class="lrcible">
                        <xsl:apply-templates select="$lrcibles[$seq]"/>
                      </td>
                    </tr>
                  </xsl:for-each>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
              <!-- listerelation colonne unique type 4, 5 ou 6 -->
              <xsl:choose>
                <xsl:when test="elemrelation">
                  <xsl:for-each select="elemrelation">
                    <xsl:variable name="seq" select="position()"/>
                    <xsl:if test="$nos">
                      <tr>
                        <td class="lrno">
                          <p>
                            <xsl:call-template name="syntaxe_texte_affichage">
                              <xsl:with-param name="texte" select="$nos[$seq]"/>
                            </xsl:call-template>
                          </p>
                        </td>
                      </tr>
                    </xsl:if>
                    <xsl:for-each select="lrsource">
                      <tr>
                        <td class="lrsource">
                          <xsl:apply-templates/>
                        </td>
                      </tr>
                    </xsl:for-each>
                    <xsl:for-each select="lrcible">
                      <tr>
                        <td class="lrcible">
                          <xsl:apply-templates/>
                        </td>
                      </tr>
                    </xsl:for-each>
                  </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:for-each select="$lrsources">
                    <xsl:variable name="seq" select="position()"/>
                    <tr>
                      <xsl:if test="$nos">
                        <td class="lrno" rowspan="2">
                          <p>
                            <xsl:call-template name="syntaxe_texte_affichage">
                              <xsl:with-param name="texte" select="$nos[$seq]"/>
                            </xsl:call-template>
                          </p>
                        </td>
                      </xsl:if>
                      <td class="lrsource">
                        <xsl:apply-templates/>
                      </td>
                    </tr>
                    <tr>
                      <td class="lrcible">
                        <xsl:apply-templates select="$lrcibles[$seq]"/>
                      </td>
                    </tr>
                  </xsl:for-each>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:otherwise>
          </xsl:choose>
        </table>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- sources -->
  <xsl:template match="source">
    <xsl:if test="text() or node()">
      <cite class="source">
        <xsl:apply-templates/>
      </cite>
    </xsl:if>
  </xsl:template>

  <!--*** APPPENDIX ***-->
  <xsl:template match="partiesann">
    <section class="{name()} col-xs-12">
      <h2 class="sr-only">{% trans 'Parties annexes' %}</h2>
      {% if content_access_granted and not only_display %}
      <xsl:apply-templates select="grannexe"/>
      {% endif %}
      <xsl:apply-templates select="merci"/>
      <xsl:apply-templates select="grnotebio"/>
      {% if content_access_granted and not only_display %}
      <xsl:apply-templates select="grnote"/>
      {% endif %}
      {% if not is_of_type_roc or only_display == 'biblio' %}
      <xsl:apply-templates select="grbiblio"/>
      {% endif %}
    </section>
  </xsl:template>

  <xsl:template match="grannexe | merci | grnotebio | grnote | grbiblio">
    <section id="{name()}" class="article-section {name()}" role="complementary">
      <xsl:if test="self::grannexe | self::merci | self::grnotebio | self::grnote">
        <h2>
          <xsl:choose>
            <xsl:when test="self::grannexe">
              <xsl:apply-templates select="self::grannexe" mode="toc-heading"/>
            </xsl:when>
            <xsl:when test="self::merci">
              <xsl:apply-templates select="self::merci" mode="toc-heading"/>
            </xsl:when>
            <xsl:when test="self::grnotebio">
              <xsl:apply-templates select="self::grnotebio" mode="toc-heading"/>
            </xsl:when>
            <xsl:when test="self::grnote">
              <xsl:apply-templates select="self::grnote" mode="toc-heading"/>
            </xsl:when>
          </xsl:choose>
        </h2>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="self::grnote">
          <ol class="unstyled">
            <xsl:apply-templates select="*[not(self::titre)]"/>
          </ol>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="*[not(self::titre)]"/>
        </xsl:otherwise>
      </xsl:choose>
    </section>
  </xsl:template>

  <!-- appendices / supplements -->
  <xsl:template match="annexe">
    <div id="{@id}" class="article-section-content" role="complementary">
      <xsl:if test="no or titre">
        <h4 class="titreann">
          <xsl:if test="titre and no">
            <xsl:apply-templates select="no"/>
            <xsl:text>. </xsl:text>
          </xsl:if>
          <xsl:if test="titre">
            <xsl:apply-templates select="titre"/>
          </xsl:if>
          <xsl:if test="no and not(titre)">
            <xsl:apply-templates select="no"/>
          </xsl:if>
        </h4>
      </xsl:if>
      <xsl:apply-templates select="section1"/>
      <xsl:apply-templates select="noteann"/>
    </div>
  </xsl:template>

  <!-- notes within appendices -->
  <xsl:template match="noteann">
    <div class="{name()}">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="noteann/no">
    <a class="renote">
      <xsl:attribute name="href">#re1
        <xsl:value-of select="../@id"/>
      </xsl:attribute>
      <xsl:attribute name="id">
        <xsl:value-of select="../@id"/>
      </xsl:attribute>
      [
      <xsl:apply-templates/>]

    </a>
  </xsl:template>

  <!-- biographical notes -->
  <xsl:template match="notebio">
    <div class="notebio">
      <xsl:apply-templates select="nompers"/>
      <xsl:apply-templates select="*[not(self::nompers)]"/>
    </div>
  </xsl:template>

  <xsl:template match="notebio/nompers">
    <h3>
      <xsl:call-template name="element_nompers_affichage">
        <xsl:with-param name="nompers" select="../nompers"></xsl:with-param>
      </xsl:call-template>
    </h3>
  </xsl:template>

  <!-- footnotes -->
  <xsl:template match="note">
    <li class="note" id="{@id}">
      <xsl:if test="no">
        <a href="#re1{@id}" class="nonote">
          <xsl:text>[</xsl:text><xsl:apply-templates select="no"/><xsl:text>]</xsl:text>
        </a>
      </xsl:if>
      <xsl:apply-templates select="*[not(self::no)]"/>
    </li>
  </xsl:template>
  <xsl:template match="renvoi">
    <xsl:element name="a">
      <xsl:attribute name="href">
        <xsl:text>#</xsl:text><xsl:value-of select="@idref"/>
      </xsl:attribute>
      <xsl:attribute name="id">
        <xsl:value-of select="@id"/>
      </xsl:attribute>
      <xsl:attribute name="class">
        <xsl:text>norenvoi</xsl:text>
      </xsl:attribute>
      <xsl:attribute name="title">
        <xsl:variable name="idref" select="@idref"/>
        <xsl:value-of select="normalize-space(substring(/article/partiesann/grnote/note[@id=$idref]/*[not(self::no)], 1, 200))"/>
        <xsl:if test="string-length(/article/partiesann/grnote/note[@id=$idref]/*[not(self::no)]) &gt; 200">
          <xsl:text>[…]</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:text>[</xsl:text>
      <xsl:value-of select="normalize-space()"/>
      <xsl:text>]</xsl:text>
    </xsl:element>
  </xsl:template>

  <xsl:template match="notefig|notetabl">
    <div class="notefigtab">
      <xsl:if test="no">
        <a href="#re1{@id}" id="{@id}" class="nonote">
          <xsl:apply-templates select="no"/>
        </a>
      </xsl:if>
      <xsl:apply-templates select="*[not(self::no)]"/>
    </div>
  </xsl:template>

  <xsl:template match="tableau//notefig|tableau//notetabl|figure//notefig|figure//notetabl">
    <div class="notefigtab">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="notefig/no|notetabl/no">
    <sup class="notefigtab" id="{../@id}">
      <xsl:apply-templates/>
    </sup>
  </xsl:template>

  <!-- bibliography -->
  <xsl:template match="biblio">
    <h2>
      <xsl:choose>
        <xsl:when test="titre">
          <xsl:value-of select="titre"/>
        </xsl:when>
        <xsl:otherwise>
          {% trans 'Bibliographie' %}
        </xsl:otherwise>
      </xsl:choose>
    </h2>
    <div class="biblio">
      <ol class="unstyled {name()}">
        <xsl:for-each select="node()[name() != '' and name() != 'titre']">
          <xsl:apply-templates select="."/>
        </xsl:for-each>
      </ol>
    </div>
  </xsl:template>

  <xsl:template match="divbiblio | subdivbiblio | sssubdivbiblio">
    <xsl:choose>
      <xsl:when test="self::divbiblio">
        <h3 class="titre"><xsl:apply-templates select="titre"/></h3>
      </xsl:when>
      <xsl:when test="self::subdivbiblio">
        <h4 class="titre"><xsl:apply-templates select="titre"/></h4>
      </xsl:when>
      <xsl:when test="self::sssubdivbiblio">
        <h5 class="titre"><xsl:apply-templates select="titre"/></h5>
      </xsl:when>
    </xsl:choose>
    <xsl:apply-templates select="*[not(self::titre)]"/>
  </xsl:template>

  <xsl:template match="refbiblio">
    <li class="{name()}"  id="{@id}">
      <xsl:apply-templates select="no"/>
      <xsl:apply-templates select="node()[name() != 'idpublic' and name() != 'no']"/>
      <div class="refbiblio-links">
        <xsl:element name="a">
          <xsl:attribute name="href">
            <xsl:text>http://scholar.google.com/scholar?q=</xsl:text>
            <xsl:apply-templates select="node()[name() != 'idpublic' and name() != 'no']"/>
          </xsl:attribute>
          <xsl:attribute name="class">
            <xsl:text>refbiblio-link scholar-link</xsl:text>
          </xsl:attribute>
          <xsl:attribute name="target">
            <xsl:text>_blank</xsl:text>
          </xsl:attribute>
          <xsl:text>Google Scholar</xsl:text>
        </xsl:element>
        <xsl:apply-templates select="idpublic"/>
      </div>
    </li>
  </xsl:template>

  <xsl:template match="refbiblio/no">
    <span class="{name()}"><xsl:apply-templates/>.&#160;</span>
  </xsl:template>

  <!--*** all-purpose typographic markup ***-->
  <xsl:template match="espacev">
    <span class="espacev {@espacetype}" style="height: {@dim}; display: block;">&#x00A0;</span>
  </xsl:template>

  <xsl:template match="espaceh">
    <span class="espaceh {@espacetype}" style="padding-left: {@dim};">&#x00A0;</span>
  </xsl:template>

  <xsl:template match="marquage">
    <xsl:choose>
      <xsl:when test="@typemarq='gras'">
        <strong>
          <xsl:apply-templates/>
        </strong>
      </xsl:when>
      <xsl:when test="@typemarq='italique'">
        <em>
          <xsl:apply-templates/>
        </em>
      </xsl:when>
      <xsl:when test="@typemarq='taillep'">
        <small>
          <xsl:apply-templates/>
        </small>
      </xsl:when>
      <xsl:otherwise>
        <span class="{@typemarq}">
          <xsl:apply-templates/>
        </span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="exposant[not(./exposant | ./renvoi)]">
    <xsl:element name="sup">
      <xsl:if test="@traitementparticulier = 'oui'">
        <xsl:attribute name="class">
          <xsl:text>{% trans "special" %}</xsl:text>
        </xsl:attribute>
      </xsl:if>
      <xsl:call-template name="syntaxe_texte_affichage">
        <xsl:with-param name="texte" select="."/>
      </xsl:call-template>
    </xsl:element>
  </xsl:template>

  <xsl:template match="indice">
    <xsl:element name="sub">
      <xsl:if test="@traitementparticulier">
        <xsl:attribute name="class">
          <xsl:text>{% trans "special" %}</xsl:text>
        </xsl:attribute>
      </xsl:if>
      <xsl:call-template name="syntaxe_texte_affichage">
        <xsl:with-param name="texte" select="."/>
      </xsl:call-template>
    </xsl:element>
  </xsl:template>

  <xsl:template match="liensimple">
    <xsl:element name="a">
      <xsl:attribute name="href">
        <xsl:value-of select="@href" xmlns:xlink="http://www.w3.org/1999/xlink" />
      </xsl:attribute>
      <xsl:attribute name="id">
        <xsl:value-of select="@id"/>
      </xsl:attribute>
      <xsl:if test="not(starts-with( @href , 'http://www.erudit.org'))">
        <xsl:attribute name="target">_blank</xsl:attribute>
      </xsl:if>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <!-- element_nompers_affichage -->
  <xsl:template name="element_nompers_affichage">
    <xsl:param name="nompers"/>
    <xsl:param name="suffixes"/>
    <xsl:if test="$nompers[@typenompers = 'pseudonyme']">
      <xsl:text> </xsl:text>
      <xsl:text>{% trans "alias" %}</xsl:text>
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:if test="$nompers/prefixe/node()">
      <xsl:call-template name="syntaxe_texte_affichage">
        <xsl:with-param name="texte" select="$nompers/prefixe"/>
      </xsl:call-template>
      <xsl:text>
      </xsl:text>
    </xsl:if>
    <xsl:if test="$nompers/prenom/node()">
      <xsl:call-template name="syntaxe_texte_affichage">
        <xsl:with-param name="texte" select="$nompers/prenom"/>
      </xsl:call-template>
    </xsl:if>
    <xsl:if test="$nompers/autreprenom/node()">
      <xsl:text>
      </xsl:text>
      <xsl:call-template name="syntaxe_texte_affichage">
        <xsl:with-param name="texte" select="$nompers/autreprenom"/>
      </xsl:call-template>
    </xsl:if>
    <xsl:if test="$nompers/nomfamille/node()">
      <xsl:text>
      </xsl:text>
      <xsl:call-template name="syntaxe_texte_affichage">
        <xsl:with-param name="texte" select="$nompers/nomfamille"/>
      </xsl:call-template>
    </xsl:if>
    <xsl:if test="$suffixes = 'true'">
      <xsl:for-each select="$nompers/suffixe[child::node()]">
        <xsl:text>, </xsl:text>
        <xsl:call-template name="syntaxe_texte_affichage">
          <xsl:with-param name="texte" select="."/>
        </xsl:call-template>
      </xsl:for-each>
    </xsl:if>
  </xsl:template>

  <!-- syntaxe_texte_affichage -->
  <xsl:template name="syntaxe_texte_affichage">
    <xsl:param name="texte" select="."/>
    <xsl:for-each select="$texte/node()">
      <xsl:choose>
        <!-- #PCDATA -->
        <xsl:when test="self::text()">
          <xsl:value-of select="."/>
        </xsl:when>
        <!-- %texte -->
        <xsl:otherwise>
          <xsl:call-template name="entite_texte_affichage">
            <xsl:with-param name="texte" select="."/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>

  <!-- entite_texte_affichage -->
  <xsl:template name="entite_texte_affichage">
    <xsl:param name="texte" select="."/>
    <xsl:apply-templates select="$texte"/>
  </xsl:template>

  <!-- noteillustrationtype -->
  <xsl:template name="noteillustrationtype">
    <xsl:param name="noteIllustration"/>
    <xsl:variable name="valeurID" select="$noteIllustration/@id"/>
    <xsl:variable name="valeurIDREF" select="concat('re1', $valeurID)"/>
    <div class="note">
      <xsl:if test="$noteIllustration/no">
        <a class="nonote" id="{$valeurID}">
          <xsl:if test="//node()[@id = $valeurIDREF]">
            <xsl:attribute name="href">
              <xsl:value-of select="concat('#', $valeurIDREF)"/>
            </xsl:attribute>
          </xsl:if>
          <xsl:text>[</xsl:text>
          <xsl:call-template name="syntaxe_texte_affichage">
            <xsl:with-param name="texte" select="$noteIllustration/no"/>
          </xsl:call-template>
          <xsl:text>]</xsl:text>
        </a>
      </xsl:if>
      <xsl:for-each select="$noteIllustration/node()[name() != '' and name() != 'no']">
        <xsl:apply-templates select="."/>
      </xsl:for-each>
    </div>
  </xsl:template>

  <!-- abstracts -->
  <xsl:template name="resume">
    <!-- abstract wrapper -->
    <xsl:element name="section">
      <xsl:attribute name="id">
        <xsl:value-of select="concat('resume-', @lang)"/>
      </xsl:attribute>
      <xsl:attribute name="class">
        <xsl:text>resume</xsl:text>
      </xsl:attribute>

      <!-- abstract title -->
      <xsl:element name="h3">
        <xsl:choose>
          <xsl:when test="title">
            <xsl:value-of select="title"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:choose>
              <xsl:when test="@lang = 'fr'">Résumé</xsl:when>
              <xsl:when test="@lang = 'en'">Abstract</xsl:when>
              <xsl:when test="@lang = 'es'">Resumen</xsl:when>
              <xsl:when test="@lang = 'de'">Zusammenfassung</xsl:when>
              <xsl:when test="@lang = 'pt'">Resumo</xsl:when>
            </xsl:choose>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:element>

      <!-- abstract content -->
      <xsl:apply-templates select="."/>

      <!-- keywords -->
      <xsl:call-template name="motscles">
        <xsl:with-param name="lang" select="@lang"/>
      </xsl:call-template>

    </xsl:element>
  </xsl:template>

  <!-- keywords -->
  <xsl:template name="motscles">
    <xsl:param name="lang"/>
    <xsl:for-each select="//grmotcle[@lang = $lang]">

      <!-- keywords wrapper -->
      <xsl:element name="div">
        <xsl:attribute name="class">
          <xsl:text>keywords</xsl:text>
        </xsl:attribute>

        <!-- keywords label -->
        <xsl:element name="p">
          <xsl:element name="strong">
            <xsl:choose>
              <xsl:when test="@lang = 'fr'">Mots-clés&#160;:</xsl:when>
              <xsl:when test="@lang = 'en'">Keywords:</xsl:when>
              <xsl:when test="@lang = 'es'">Palabras clave:</xsl:when>
              <xsl:when test="@lang = 'de'">Stichworte:</xsl:when>
              <xsl:when test="@lang = 'pt'">Palavras chaves:</xsl:when>
            </xsl:choose>
          </xsl:element>
        </xsl:element>

        <!-- keywords list -->
        <xsl:element name="ul">
          <xsl:for-each select="motcle">
            <xsl:element name="li">
              <xsl:attribute name="class">
                <xsl:text>keyword</xsl:text>
              </xsl:attribute>
              <xsl:apply-templates select="."/><xsl:if test="position() != last()">, </xsl:if>
            </xsl:element>
          </xsl:for-each>
        </xsl:element>

      </xsl:element>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
