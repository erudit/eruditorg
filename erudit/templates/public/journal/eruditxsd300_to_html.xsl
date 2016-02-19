<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output method="html" indent="yes" encoding="UTF-8"/>
	<xsl:strip-space elements="*"/>

	<!--=========== VARIABLES & PARAMETERS ===========-->
    <!-- possible values for cover - 'no', 'coverpage.jpg', 'no-image' -->
    <xsl:variable name="iderudit" select="article/@idproprio"/>
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
	<xsl:variable name="uriStart">http://id.erudit.org/iderudit/</xsl:variable>
	<xsl:variable name="doiStart">http://dx.doi.org/</xsl:variable>
	<xsl:variable name="urlSavant">http://erudit.org/revue/</xsl:variable>
	<xsl:variable name="urlCulturel">http://erudit.org/culture/</xsl:variable>

	<!--=========== RESULT-DOCUMENT ===========-->
	<!-- Savante, culturelle, ... -->
	<xsl:param name="typecoll" />

	<!-- Eliminer les lignes vides dans le document resultant -->
	<xsl:strip-space elements="alinea"/>

	<xsl:template match="/">
		<div class="article-wrapper">
			<xsl:apply-templates select="article"/>
		</div>
	</xsl:template>

	<xsl:template match="article">

		<!-- main header for article -->
		<header class="row article-header">

			<hgroup class="col-xs-12 child-column-fit border-top">

				<aside class="col-sm-8">
					<h2>
						<xsl:if test="liminaire/grtitre/titre">
							<xsl:apply-templates select="liminaire/grtitre/titre"/>
						</xsl:if>
					</h2>
					<h3>
						<xsl:if test="liminaire/grtitre/sstitre">
							<xsl:apply-templates select="liminaire/grtitre/sstitre"/>
						</xsl:if>
						<xsl:if test="liminaire/grtitre/trefbiblio">
							<xsl:apply-templates select="liminaire/grtitre/trefbiblio"/>
						</xsl:if>
					</h3>
				</aside>

				<!-- TODO: cover image -->
				<aside class="col-sm-4">
					<figure class="journal-logo">
						<img src="http://www.erudit.org/revue/logosmall/erudit:erudit.rse22.jpg" alt="Couverture du numéro" class="img-responsive"/>
					</figure>
				</aside>

			</hgroup>

			<!-- meta authors -->
			<hgroup class="meta-authors col-sm-6 border-top">

				<xsl:apply-templates select="liminaire/grauteur/auteur"/>

				<dl class="mono-space idpublic">
					<dt>URI</dt>
					<dd>
						<a href="{$uriStart}{$iderudit}">
							<xsl:value-of select="$uriStart"/>
							<xsl:value-of select="$iderudit"/>
						</a>
					</dd>
					<dt>DOI</dt>
					<dd>
						<a href="{$doiStart}10.7202/{$iderudit}">
							10.7202/<xsl:value-of select="$iderudit"/>
						</a>
					</dd>
				</dl>

				<xsl:apply-templates select="admin/droitsauteur"/>

			</hgroup>

			<!-- meta magazine -->
			<hgroup class="meta-magazine col-sm-6 border-top">

				<h4>
					<xsl:apply-templates select="../article/@typeart"/> de la revue
					<a href="{$urlSavant}{$titreAbrege}">
						<xsl:value-of select="admin/revue/titrerev"/>
					</a>
				</h4>

				<xsl:value-of select="admin/numero/grtheme/theme"/>
				<xsl:apply-templates select="admin/numero" mode="refpapier"/>


			</hgroup>


		</header>

		<!-- <hr/> -->

		<!--=== plan de l'article ===-->
		<div class="row article-body border-top">
			<xsl:if test="//corps">
				<aside class="col-md-4">
					<section class="planarticle">
						<h2>Plan de l’article</h2>
						<nav>
							<ul>
								<li class="debutArticle">
									<a href="#">
										<em>À propos de cet article</em>
									</a>
								</li>
								<xsl:if test="//resume">
									<li>
										<a href="#resume">Résumé</a>
									</li>
								</xsl:if>
								<xsl:apply-templates select="corps/section1/titre[not(@traitementparticulier='oui')]" mode="html_toc"/>
								<xsl:if test="//grannexe">
									<li>
										<a href="#grannexe">
											<xsl:apply-templates select="//grannexe" mode="heading"/>
										</a>
									</li>
								</xsl:if>
								<xsl:if test="//merci">
									<li>
										<a href="#merci">
											<xsl:apply-templates select="//merci" mode="heading"/>
										</a>
									</li>
								</xsl:if>
								<xsl:if test="//grnotebio">
									<li>
										<a href="#grnotebio">
											<xsl:apply-templates select="//grnotebio" mode="heading"/>
										</a>
									</li>
								</xsl:if>
								<xsl:if test="//grnote">
									<li>
										<a href="#grnote">
											<xsl:apply-templates select="//grnote" mode="heading"/>
										</a>
									</li>
								</xsl:if>
								<xsl:if test="//grbiblio">
									<li>
										<a href="#grbiblio">
											<xsl:apply-templates select="//grbiblio" mode="heading"/>
										</a>
									</li>
								</xsl:if>
							</ul>
						</nav>
					</section>
				</aside>
			</xsl:if>
			<aside class="col-md-8">

				<!-- ********* Resume ******** -->
				<xsl:apply-templates select="//resume"/>

				<!-- ********* Corps ******** -->
				<xsl:apply-templates select="corps"/>

				<!-- ********* parties annexes ******** -->
				<xsl:apply-templates select="partiesann[node()]"/>

				<!-- ********* listes figures / tableaux  ******** -->
				<section id="listes" class="listes">

				  <xsl:if test="//tableau">
					<article id="tableau">
					  <h4>Liste des tableaux</h4>
					  <xsl:apply-templates select="//tableau/objetmedia" mode="liste"/>
					</article>
				  </xsl:if>

				  <xsl:if test="//figure">
					<article id="figure">
					  <h4>Liste des figures</h4>
					  <xsl:apply-templates select="//figure/objetmedia" mode="liste"/>
					</article>
				  </xsl:if>

				</section>

			</aside>
		</div>


	</xsl:template>

	<!--=========== TEMPLATES ===========-->

	<!--====== CORPS ======-->
	<xsl:template match="corps">
		<section class="{name()}">
			<h4>Texte</h4>
			<xsl:apply-templates/>
		</section>
	</xsl:template>

	<xsl:template match="section1">
		<a id="{@id}">
			<xsl:text>
			</xsl:text>
		</a>
		<xsl:if test="titre">
			<xsl:element name="h2">
				<xsl:if test="titre/@traitementparticulier">
					<xsl:attribute name="class">special</xsl:attribute>
				</xsl:if>
				<xsl:apply-templates select="titre"/>
			</xsl:element>
		</xsl:if>
		<xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
	</xsl:template>
	<xsl:template match="section2">
	<a id="{@id}">
		<xsl:text>
		</xsl:text>
		</a>
		<xsl:if test="titre">
			<xsl:element name="h3">
				<xsl:if test="titre/@traitementparticulier">
					<xsl:attribute name="class">special</xsl:attribute>
				</xsl:if>
				<xsl:apply-templates select="titre"/>
			</xsl:element>
		</xsl:if>
		<xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
	</xsl:template>
	<xsl:template match="section3">
		<a id="{@id}">
			<xsl:text>
			</xsl:text>
		</a>
		<xsl:if test="titre">
			<xsl:element name="h4">
				<xsl:if test="titre/@traitementparticulier">
					<xsl:attribute name="class">special</xsl:attribute>
				</xsl:if>
				<xsl:apply-templates select="titre"/>
			</xsl:element>
		</xsl:if>
		<xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
	</xsl:template>
	<xsl:template match="section4">
		<a id="{@id}">
			<xsl:text>
			</xsl:text>
		</a>
		<xsl:if test="titre">
			<xsl:element name="h5">
				<xsl:if test="titre/@traitementparticulier">
					<xsl:attribute name="class">special</xsl:attribute>
				</xsl:if>
				<xsl:apply-templates select="titre"/>
			</xsl:element>
		</xsl:if>
		<xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
	</xsl:template>
	<xsl:template match="section5">
		<a id="{@id}">
			<xsl:text>
			</xsl:text>
		</a>
		<xsl:if test="titre">
			<xsl:element name="h6">
				<xsl:if test="titre/@traitementparticulier">
					<xsl:attribute name="class">special</xsl:attribute>
				</xsl:if>
				<xsl:apply-templates select="titre"/>
			</xsl:element>
		</xsl:if>
		<xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
	</xsl:template>
	<xsl:template match="section6">
		<a id="{@id}">
			<xsl:text>
			</xsl:text>
		</a>
		<xsl:if test="titre">
			<xsl:element name="h6">
				<xsl:attribute name="class">h7</xsl:attribute>
				<xsl:if test="titre/@traitementparticulier">
					<xsl:attribute name="class">special</xsl:attribute>
				</xsl:if>
				<xsl:apply-templates select="titre"/>
			</xsl:element>
		</xsl:if>
		<xsl:apply-templates select="*[not(self::no)][not(self::titre)][not(self::titreparal)]"/>
	</xsl:template>
	<xsl:template match="para">
		<p class="para">
			<xsl:apply-templates select="no" mode="para"/>
			<xsl:apply-templates select="*[not(self::no)]"/>
		</p>
	</xsl:template>
	<xsl:template match="alinea">
		<p class="alinea">
			<xsl:apply-templates/>
		</p>
	</xsl:template>
	<xsl:template match="no" mode="para">
		<div class="nopara">
			<xsl:apply-templates/>
			<xsl:text>
			</xsl:text>
		</div>
	</xsl:template>
	<xsl:template match="section1/alinea|section2/alinea|section3/alinea|section4/alinea|section5/alinea|section6/alinea|grannexe/alinea"  priority="1">
		<p class="horspara">
			<xsl:apply-templates/>
		</p>
	</xsl:template>
	<xsl:template match="no">
		<span class="no">
			<xsl:apply-templates/>
		</span>
	</xsl:template>
	<xsl:template match="no" mode="liste">
		<span class="no">
			<xsl:apply-templates select="*[not(self::renvoi)]"/>
		</span>
	</xsl:template>
	<xsl:template match="legende/titre | legende/sstitre">
		<div class="legende">
		<xsl:for-each select=".">
			<div class="{name()}">
				<xsl:apply-templates/>
			</div>
		</xsl:for-each>
		</div>
	</xsl:template>
	<xsl:template match="legende/titre | legende/sstitre" mode="liste">
		<div class="legende">
		<xsl:for-each select=".">
			<div class="{name()}">
				<xsl:apply-templates select="*[not(self::renvoi)]"/>
			</div>
		</xsl:for-each>
		</div>
	</xsl:template>
	<xsl:template match="ligne">
		<xsl:apply-templates/>
		<br/>
	</xsl:template>
	<xsl:template match="titre">
		<span class="titre">
			<xsl:apply-templates/>
		</span>
	</xsl:template>
	<xsl:template match="elemliste">
		<li>
			<xsl:apply-templates/>
		</li>
	</xsl:template>
	<!-- bloccitation -->
	<xsl:template match="bloccitation">
		<blockquote>
			<xsl:apply-templates/>
		</blockquote>
	</xsl:template>
	<!-- dedicace, epigraphe -->
	<xsl:template match="dedicace|epigraphe">
		<div class="{name()}">
			<xsl:apply-templates/>
		</div>
	</xsl:template>
	<!-- verbatim -->
	<xsl:template match="verbatim">
		<div class="verbatim {@typeverb}">
			<xsl:apply-templates/>
		</div>
	</xsl:template>
	<!-- bloc -->
	<xsl:template match="bloc">
		<div class="bloc">
			<xsl:apply-templates/>
		</div>
	</xsl:template>
	<!-- grfigure, grtableau, figure & tableau -->
	<xsl:template match="grfigure|grtableau">
		<div class="{name()}">
			<xsl:apply-templates/>
		</div>
	</xsl:template>
	<xsl:template match="figure|tableau">
		<!-- makes sure that there is only one image displayed for a figure or tableau div -->
		<figure class="{name()}">
			<xsl:apply-templates select="objetmedia"/>
		</figure>
	</xsl:template>
	<xsl:template match="figure/objetmedia|tableau/objetmedia">
		<xsl:variable name="imgId" select="image/@id"/>
		<xsl:variable name="nomImg" select="$infoimg/infoDoc/im[@id=$imgId]/imPlGr/nomImg"/>
		<figure class="{name(..)}">
			<img src="../images/{$nomImg}" title="{normalize-space(../legende)}" alt="{normalize-space(../legende)}"/>
			<figcaption>
				<a id="{../@id}">
					<xsl:text>
					</xsl:text>
				</a>
				<xsl:apply-templates select="../no"/>
				<xsl:apply-templates select="../legende/titre | ../legende/sstitre"/>
				<span class="voirliste">
					(<a href="#li{../@id}">Voir la liste des <xsl:if test="parent::figure">figures</xsl:if><xsl:if test="parent::tableau">tableaux</xsl:if></a>)
				</span>
				<xsl:apply-templates select="../legende/alinea | ../legende/bloccitation | ../legende/listenonord | ../legende/listeord | ../legende/listerelation | ../legende/objetmedia | ../legende/refbiblio | ../legende/tabtexte | ../legende/verbatim"/>
				<xsl:apply-templates select="../notefig|../notetabl"/>
				<xsl:apply-templates select="../source"/>
			</figcaption>
		</figure>
	</xsl:template>
	<!-- grencadre, grequation, grexemple, encadre, equation & exemple -->
	<xsl:template match="grencadre|grequation|grexemple">
		<aside class="{name()}">
			<xsl:apply-templates select="no"/>
			<xsl:apply-templates select="legende"/>
			<xsl:apply-templates select="*[not(self::no)][not(self::legende)][not(self::titreparal)]"/>
		</aside>
	</xsl:template>
	<xsl:template match="encadre">
		<aside class="encadre type{@type}">
			<xsl:apply-templates/>
		</aside>
	</xsl:template>
	<!-- noteenc | noteeq | noteex -->
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
	<xsl:template match="exemple">
		<aside class="exemple">
			<xsl:apply-templates select="no"/>
			<xsl:apply-templates select="legende"/>
			<xsl:for-each select="node()[name() != '' and name() != 'no' and name() != 'legende']">
				<xsl:apply-templates select="."/>
			</xsl:for-each>
		</aside>
	</xsl:template>
	<!-- objetmedia -->
	<xsl:template match="objetmedia/audio">
		<xsl:variable name="nomAud" select="@*[local-name()='href']"/>
		<audio id="{@id}" preload="metadata" controls="controls">
			<source src="http://erudit.org/media/{$titreAbrege}/{$iderudit}/{$nomAud}" type="{@typemime}"/>
		</audio>
	</xsl:template>
	<xsl:template match="objetmedia/image">
		<xsl:variable name="nomImg" select="@*[local-name()='href']"/>
		<span class="lien_img">
			<img src="../images/{$nomImg}" class="objetmedia_img"/>
		</span>
	</xsl:template>
	<xsl:template match="objetmedia/texte">
		<div class="objetTexte">
			<xsl:apply-templates/>
		</div>
	</xsl:template>
	<xsl:template match="objetmedia/video">
		<xsl:variable name="videohref" select="@*[local-name()='href']"/>
		<xsl:variable name="nomVid" select="substring-before($videohref, '.')"/>
		<video id="{@id}" preload="metadata" controls="controls">
			<source src="http://erudit.org/media/{$titreAbrege}/{$iderudit}/{$nomVid}.mp4" type="video/mp4"/>
		</video>
	</xsl:template>
	<!-- grobjet & objet -->
	<xsl:template match="grobjet">
		<xsl:apply-templates/>
	</xsl:template>
	<xsl:template match="objet">
		<div class="objet">
			<xsl:apply-templates/>
		</div>
	</xsl:template>
	<!-- listenonord -->
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
	<!-- listeord -->
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
	<!-- listerelation -->
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
	                          <td class="header">
	                              <xsl:apply-templates/>
	                          </td>
	                      </xsl:for-each>
	                      <xsl:for-each select="lrciblee">
	                          <td class="header">
	                              <xsl:apply-templates/>
	                          </td>
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
	<!-- tabtexte -->
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
	          <xsl:value-of select="concat( 'tabtexte type', $type )"/>
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
	      <xsl:attribute name="id">
	          <xsl:value-of select="$id"/>
	      </xsl:attribute>
	  </xsl:if>
	  <xsl:if test="$identete">
	      <xsl:attribute name="headers">
	          <xsl:value-of select="$identete"/>
	      </xsl:attribute>
	  </xsl:if>
	  <xsl:if test="$nbcol">
	      <xsl:choose>
	          <xsl:when test="$noeudTab/self::tabgrcol">
	              <xsl:attribute name="colspan">
	                  <xsl:value-of select="$nbcol"/>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:otherwise>
	              <xsl:attribute name="colspan">
	                  <xsl:value-of select="$nbcol"/>
	              </xsl:attribute>
	          </xsl:otherwise>
	      </xsl:choose>
	  </xsl:if>
	  <xsl:if test="$nbligne">
	      <xsl:attribute name="rowspan">
	          <xsl:value-of select="$nbligne"/>
	      </xsl:attribute>
	  </xsl:if>
	  <xsl:if test="$portee">
	      <xsl:choose>
	          <xsl:when test="$portee = 'ligne'">
	              <xsl:attribute name="scope">
	                  <xsl:text>row</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$portee = 'colonne'">
	              <xsl:attribute name="scope">
	                  <xsl:text>col</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$portee = 'grligne'">
	              <xsl:attribute name="scope">
	                  <xsl:text>rowgroup</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$portee = 'grcolonne'">
	              <xsl:attribute name="scope">
	                  <xsl:text>colgroup</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	      </xsl:choose>
	  </xsl:if>
	  <xsl:if test="$alignh">
	      <xsl:choose>
	          <xsl:when test="$alignh = 'gauche'">
	              <xsl:attribute name="style">
	                  <xsl:text>text-align: left;</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$alignh = 'centre'">
	              <xsl:attribute name="style">
	                  <xsl:text>text-align: center;</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$alignh = 'droite'">
	              <xsl:attribute name="style">
	                  <xsl:text>text-align: right;</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$alignh = 'justifie'">
	              <xsl:attribute name="style">
	                  <xsl:text>text-align: justify;</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$alignh = 'carac'">
	              <xsl:attribute name="style">
	                  <xsl:text>char</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	      </xsl:choose>
	  </xsl:if>
	  <xsl:if test="$carac">
	      <xsl:attribute name="char">
	          <xsl:value-of select="$carac"/>
	      </xsl:attribute>
	  </xsl:if>
	  <xsl:if test="$alignv">
	      <xsl:choose>
	          <xsl:when test="$alignv = 'haut'">
	              <xsl:attribute name="style">
	                  <xsl:text>vertical-align: top;</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$alignv = 'centre'">
	              <xsl:attribute name="style">
	                  <xsl:text>vertical-align: middle;</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$alignv = 'bas'">
	              <xsl:attribute name="style">
	                  <xsl:text>vertical-align: bottom;</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	          <xsl:when test="$alignv = 'lignebase'">
	              <xsl:attribute name="style">
	                  <xsl:text>vertical-align: baseline;</xsl:text>
	              </xsl:attribute>
	          </xsl:when>
	      </xsl:choose>
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
	        <xsl:apply-templates/>
	        <!-- tabcol* -->
	    </xsl:element>
	</xsl:template>
	<xsl:template match="tabentete">
	    <xsl:element name="thead">
	        <xsl:call-template name="tradAttr">
	            <xsl:with-param name="noeudTab" select="."/>
	        </xsl:call-template>
	        <xsl:apply-templates/>
	        <!-- tabligne+ -->
	    </xsl:element>
	</xsl:template>
	<xsl:template match="tabligne">
	    <xsl:element name="tr">
	        <xsl:call-template name="tradAttr">
	            <xsl:with-param name="noeudTab" select="."/>
	        </xsl:call-template>
	        <xsl:apply-templates/>
	        <!-- (tabcellulee | tabcelluled)+ -->
	    </xsl:element>
	</xsl:template>
	<xsl:template match="tabcelluled">
	    <xsl:element name="td">
	        <xsl:call-template name="tradAttr">
	            <xsl:with-param name="noeudTab" select="."/>
	        </xsl:call-template>
	        <xsl:apply-templates/>
	        <!-- blocimbrique+ -->
	    </xsl:element>
	</xsl:template>
	<xsl:template match="tabcellulee">
	    <xsl:element name="th">
	        <xsl:call-template name="tradAttr">
	            <xsl:with-param name="noeudTab" select="."/>
	        </xsl:call-template>
	        <xsl:apply-templates/>
	        <!-- blocimbrique+ -->
	    </xsl:element>
	</xsl:template>
	<xsl:template match="tabpied">
	    <xsl:element name="tfoot">
	        <xsl:call-template name="tradAttr">
	            <xsl:with-param name="noeudTab" select="."/>
	        </xsl:call-template>
	        <xsl:apply-templates/>
	        <!-- tabligne+ -->
	    </xsl:element>
	</xsl:template>
	<xsl:template match="tabgrligne">
	    <xsl:element name="tbody">
	        <xsl:call-template name="tradAttr">
	            <xsl:with-param name="noeudTab" select="."/>
	        </xsl:call-template>
	        <xsl:apply-templates/>
	        <!-- tabligne+ -->
	    </xsl:element>
	</xsl:template>
	<xsl:template match="source">
	    <xsl:if test="text() or node()">
	        <div class="source">
	            <xsl:apply-templates/>
	        </div>
	    </xsl:if>
	</xsl:template>

  <!--=== PARTIESANN ===-->
  <xsl:template match="partiesann">
    <section id="partiesann">
        <xsl:apply-templates/>
    </section>
  </xsl:template>

  <xsl:template match="grannexe | merci | grnotebio | grnote | grbiblio">
      <div id="{name()}">
          <h1>
              <xsl:choose>
                  <xsl:when test="self::grannexe">
                      <xsl:apply-templates select="self::grannexe" mode="heading"/>
                  </xsl:when>
                  <xsl:when test="self::merci">
                      <xsl:apply-templates select="self::merci" mode="heading"/>
                  </xsl:when>
                  <xsl:when test="self::grnotebio">
                      <xsl:apply-templates select="self::grnotebio" mode="heading"/>
                  </xsl:when>
                  <xsl:when test="self::grnote">
                      <xsl:apply-templates select="self::grnote" mode="heading"/>
                  </xsl:when>
                  <xsl:when test="self::grbiblio">
                      <xsl:apply-templates select="self::grbiblio" mode="heading"/>
                  </xsl:when>
              </xsl:choose>
          </h1>
          <xsl:apply-templates select="*[not(self::titre)]"/>
      </div>
  </xsl:template>
  <!-- annexe -->
  <xsl:template match="annexe">
      <div class="annexe">
          <xsl:if test="no or titre">
              <h2 class="titreann">
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
              </h2>
          </xsl:if>
          <xsl:apply-templates select="section1"/>
          <xsl:apply-templates select="noteann"/>
      </div>
  </xsl:template>
  <!-- notebio -->
  <xsl:template match="notebio">
      <div class="notebio">
          <xsl:apply-templates/>
      </div>
  </xsl:template>
  <xsl:template match="notebio/nompers">
      <h2 class="nompers">
          <xsl:apply-templates/>
      </h2>
  </xsl:template>
  <!-- note -->
  <xsl:template match="note">
      <div class="note" id="{@id}">
          <xsl:if test="no">
              <a href="#re1{@id}" class="nonote">
                  <xsl:text>[</xsl:text>
                  <xsl:apply-templates select="no"/>
                  <xsl:text>] </xsl:text>
              </a>
          </xsl:if>
          <xsl:apply-templates select="alinea" mode="numero"/>
          <xsl:apply-templates select="*[not(self::alinea)][not(self::no)]"/>
      </div>
  </xsl:template>
  <xsl:template match="alinea" mode="numero">
      <span class="alinea">
          <xsl:apply-templates/>
      </span>
  </xsl:template>
  <xsl:template match="renvoi">
      <xsl:text>&#160;</xsl:text>
      <a href="#{@idref}" id="{@id}" class="norenvoi">
          <xsl:text>[</xsl:text>
          <xsl:apply-templates/>
          <xsl:text>]</xsl:text>
      </a>
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
          <xsl:if test="no">
              <xsl:apply-templates select="no"/>
          </xsl:if>
          <xsl:apply-templates select="*[not(self::no)]"/>
      </div>
  </xsl:template>
  <xsl:template match="notefig/no|notetabl/no">
      <sup class="notefigtab">
          <xsl:apply-templates/>
      </sup>
  </xsl:template>
  <!-- noteann -->
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
  <!-- biblio -->
  <xsl:template match="biblio">
      <div class="{name()}">
          <xsl:apply-templates/>
      </div>
  </xsl:template>
  <xsl:template match="divbiblio">
      <div class="divbiblio">
          <xsl:apply-templates/>
      </div>
  </xsl:template>
  <xsl:template match="biblio/titre">
      <h2 class="{name()}">
          <xsl:apply-templates/>
      </h2>
  </xsl:template>
  <xsl:template match="refbiblio">
      <xsl:variable name="valeurNO" select="no"/>
      <div class="refbiblio">
          <a class="no" id="{@id}">
              <xsl:choose>
                  <xsl:when test="$valeurNO">
                      <xsl:apply-templates select="$valeurNO"/>
                      <xsl:text>.</xsl:text>
                  </xsl:when>
                  <xsl:otherwise>&#x00A0;</xsl:otherwise>
              </xsl:choose>
          </a>
          <xsl:apply-templates select="node()[name() != 'idpublic' and name() != 'no']"/>
          <xsl:text></xsl:text>
          <xsl:apply-templates select="idpublic"/>
      </div>
  </xsl:template>

<!--=== LISTE TAB / LISTE FIG ===-->
<xsl:template match="tableau/objetmedia | figure/objetmedia" mode="liste">
    <xsl:variable name="imgId" select="image/@id"/>
    <xsl:variable name="nomImg" select="$infoimg/infoDoc/im[@id=$imgId]/imPlGr/nomImg"/>
    <xsl:variable name="imgwidth" select="$infoimg/infoDoc/im[@id=$imgId]/imPlGr/dimx"/>
    <xsl:for-each select=".">
        <figure class="{name(..)}" id="li{../@id}">
            <img src="../images/{$nomImg}" title="{normalize-space(../legende)}" alt="{normalize-space(../legende)}"/>
            <figcaption class="notitre">
                <xsl:apply-templates select="../no" mode="liste"/>
                <xsl:apply-templates select="../legende/titre" mode="liste"/>
                <!-- s'il y a des renvois dans la source ou la légende, plusieurs IDs sont créés. -->
                <span class="allertexte">[
                    <a href="#{../@id}">Aller au texte</a>]
                </span>
            </figcaption>
        </figure>
    </xsl:for-each>
</xsl:template>
<!-- espacev -->
<xsl:template match="espacev">
    <div class="espacev" style="height: {@dim}">&#x00A0;</div>
</xsl:template>
<!-- espaceh -->
<xsl:template match="espaceh">
    <span class="espaceh" style="padding-left: {@dim}">&#x00A0;</span>
</xsl:template>
<!-- marquage -->
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
<xsl:template match="exposant">
    <xsl:element name="sup">
        <xsl:if test="@traitementparticulier = 'oui'">
            <xsl:attribute name="class">
                <xsl:text>special</xsl:text>
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
                <xsl:text>special</xsl:text>
            </xsl:attribute>
        </xsl:if>
        <xsl:call-template name="syntaxe_texte_affichage">
            <xsl:with-param name="texte" select="."/>
        </xsl:call-template>
    </xsl:element>
</xsl:template>


<!-- marquage pour plan -->
<xsl:template match="marquage" mode="html_toc">
  <span class="{@typemarq}">
	  <xsl:apply-templates/>
  </span>
</xsl:template>
<xsl:template match="exposant" mode="html_toc">
  <xsl:element name="sup">
	  <xsl:if test="@traitementparticulier = 'oui'">
		  <xsl:attribute name="class">
			  <xsl:text>special</xsl:text>
		  </xsl:attribute>
	  </xsl:if>
	  <xsl:call-template name="syntaxe_texte_affichage">
		  <xsl:with-param name="texte" select="."/>
	  </xsl:call-template>
  </xsl:element>
</xsl:template>
<xsl:template match="indice" mode="html_toc">
  <xsl:element name="sub">
	  <xsl:if test="@traitementparticulier">
		  <xsl:attribute name="class">
			  <xsl:text>special</xsl:text>
		  </xsl:attribute>
	  </xsl:if>
	  <xsl:call-template name="syntaxe_texte_affichage">
		  <xsl:with-param name="texte" select="."/>
	  </xsl:call-template>
  </xsl:element>
</xsl:template>
<!-- idpublic -->
<xsl:template match="idpublic[@scheme = 'doi']">
  <xsl:text>&#x0020;</xsl:text>
  <a href="{$doiStart}{.}">
	  <xsl:if test="contains( . , '10.7202')">
		  <img src="../images/iconeErudit.png" title="ID public Érudit" alt="Icône pour les ID publics Érudit"/>
	  </xsl:if>
	  <xsl:text>DOI:</xsl:text>
	  <xsl:value-of select="."/>
  </a>
</xsl:template>
<xsl:template match="idpublic[@scheme='uri']">
  <a href="{$uriStart}{.}">
	  <xsl:text>URI:</xsl:text>
	  <xsl:value-of select="."/>
  </a>
</xsl:template>
<xsl:template match="liensimple">
  <a href="{@href}">
	  <xsl:value-of select="."/>
  </a>
</xsl:template>

	<xsl:template match="@typeart">
		<xsl:choose>
			<xsl:when test="$typeudoc = 'article'">Un article</xsl:when>
			<xsl:when test="$typeudoc = 'compterendu'">Un compte rendu</xsl:when>
			<xsl:when test="$typeudoc = 'note'">Une note</xsl:when>
			<xsl:otherwise>Un document</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="article/liminaire/grtitre/titre | article/liminaire/grtitre/sstitre | article/liminaire/grtitre/trefbiblio" mode="title">
		<xsl:value-of select="normalize-space(.)"/>
	</xsl:template>

	<xsl:template match="grauteur/auteur">
		<div class="author">
			<xsl:apply-templates select="*" mode="lim"/>
		</div>
	</xsl:template>

	<xsl:template match="auteur">
		<span class="{name()}">
			<xsl:value-of select="."/>
		</span>
	</xsl:template>

	<xsl:template match="auteur/nompers" mode="lim">
		<xsl:if test="child::node()/child::text()">
			<h3 class="{name()}">
				<xsl:call-template name="element_nompers_affichage">
					<xsl:with-param name="nompers" select="."/>
				</xsl:call-template>
			</h3>
		</xsl:if>
	</xsl:template>

	<xsl:template match="prefixe | prenom | autreprenom | nomfamille | suffixe">
		<xsl:apply-templates/>
		<xsl:if test="position() != last()">
			<xsl:text>
			</xsl:text>
		</xsl:if>
	</xsl:template>

	<xsl:template match="auteur/affiliation" mode="lim">
		<h4 class="affiliation">
			<xsl:apply-templates select="fonction"/>
			<xsl:apply-templates select="divorg"/>
			<xsl:apply-templates select="nomorg"/>
			<xsl:apply-templates select="adresse"/>
			<xsl:apply-templates select="alinea"/>
		</h4>
	</xsl:template>

	<xsl:template match="admin//membre | admin//fonction | admin//divorg | admin//nomorg | admin//adresse | article//affiliation/alinea" mode="lim">
    <div class="{name()}">
      <xsl:apply-templates/>
      <xsl:text>
      </xsl:text>
    </div>
  </xsl:template>

	<!-- element_nompers_affichage -->
	<xsl:template name="element_nompers_affichage">
		<xsl:param name="nompers"/>
		<xsl:if test="$nompers[@typenompers = 'pseudonyme']">
			<xsl:text>alias</xsl:text>
			<xsl:text>
			</xsl:text>
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
		<xsl:for-each select="$nompers/suffixe[child::node()]">
			<xsl:text>, </xsl:text>
			<xsl:call-template name="syntaxe_texte_affichage">
				<xsl:with-param name="texte" select="."/>
			</xsl:call-template>
		</xsl:for-each>
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

	<!-- numpublication -->
	<xsl:template match="admin/numero" mode="refpapier">
		<h4 class="volumaison">
			<xsl:for-each select="volume | nonumero[1] | pub/periode | pub/annee | pagination">
				<xsl:apply-templates select="."/>
				<xsl:if test="position() != last()">
					<xsl:text>, </xsl:text>
				</xsl:if>
			</xsl:for-each>
		</h4>
	</xsl:template>
	<xsl:template match="numero/volume">
		<span class="{name()}">
			<xsl:text>Volume&#160;</xsl:text>
			<xsl:value-of select="."/>
		</span>
	</xsl:template>
	<xsl:template match="numero/nonumero[1]">
		<!-- template for first occurence of nonumero only; this allows the display of issues like Numéro 3-4 or Numéro 1-2-3 -->
		<span class="{name()}">
			<xsl:text>Numéro&#160;</xsl:text>
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
      <span class="{name()}">
        <xsl:choose>
          <xsl:when test="ppage = dpage">p.&#160;<xsl:value-of select="ppage"/></xsl:when>
          <xsl:otherwise>pp.&#160;<xsl:value-of select="ppage"/>–<xsl:value-of select="dpage"/></xsl:otherwise>
        </xsl:choose>
      </span>
    </xsl:template>
    <xsl:template match="ppage|dpage">
      <span class="{name()}">
        <xsl:value-of select="."/>
      </span>
    </xsl:template>

	<!-- droitauteur -->
    <xsl:template match="droitsauteur">
      <h4 class="{name()}">
        <xsl:apply-templates/>
      </h4>
    </xsl:template>

	<!-- resume -->
	<xsl:template match="//resume">
		<div id="{name()}" class="{name()}">
			<xsl:if test="@lang='fr'">
				<h4>Résumé</h4>
				<xsl:apply-templates/>
				<xsl:if test="//grmotcle[@lang='fr']/motcle">
					<footer class="keywords">
						<h5 class="etiquette">Mots clés : </h5>
						<xsl:for-each select="//grmotcle[@lang='fr']/motcle">
							<xsl:apply-templates/>
							<xsl:if test="position() != last()">
								<span class="keyword"><xsl:text>, </xsl:text></span>
							</xsl:if>
						</xsl:for-each>
					</footer>
				</xsl:if>
			</xsl:if>
			<xsl:if test="@lang='en'">
				<h4>Abstract</h4>
				<xsl:apply-templates select="//grtitre/grtitreparal/titreparal[@lang='en']" mode="lim"/>
				<xsl:apply-templates select="alinea"/>
				<xsl:if test="//grmotcle[@lang='en']/motcle">
					<footer class="keywords">
					<h5 class="etiquette">Keywords : </h5>
					<xsl:for-each select="//grmotcle[@lang='en']/motcle">
						<xsl:apply-templates/>
						<xsl:if test="position() != last()">
							<xsl:text>, </xsl:text>
						</xsl:if>
					</xsl:for-each>
					</footer>
				</xsl:if>
			</xsl:if>
			<xsl:if test="@lang='es'">
				<h4>Resumen</h4>
				<xsl:apply-templates select="//grtitre/grtitreparal/titreparal[@lang='es']" mode="lim"/>
				<xsl:apply-templates select="alinea"/>
				<xsl:apply-templates/>
				<xsl:if test="//grmotcle[@lang='es']/motcle">
					<div class="motcle">
						<span class="etiquette">Palabras clave : </span>
						<xsl:for-each select="//grmotcle[@lang='es']/motcle">
							<xsl:apply-templates/>
							<xsl:if test="position() != last()">
								<xsl:text>, </xsl:text>
							</xsl:if>
						</xsl:for-each>
					</div>
				</xsl:if>
			</xsl:if>
		</div>
		<hr/>
	</xsl:template>
	<xsl:template match="resume/alinea">
		<xsl:apply-templates/>
	</xsl:template>

	<!-- toc -->
    <xsl:template match="article/corps/section1/titre[not(@traitementparticulier='oui')]" mode="html_toc">
      <li>
        <a href="#{../@id}">
          <xsl:apply-templates mode="html_toc"/>
        </a>
      </li>
    </xsl:template>
	<xsl:template match="grannexe | grnotebio | grnote | merci | grbiblio"  mode="heading">
		<xsl:if test="self::grannexe">
			<xsl:choose>
				<xsl:when test="titre">
					<xsl:value-of select="titre"/>
				</xsl:when>
				<xsl:when test="count(annexe) = 1">Annexe</xsl:when>
				<xsl:otherwise>Annexes</xsl:otherwise>
			</xsl:choose>
		</xsl:if>
		<xsl:if test="self::grnotebio">
				<xsl:choose>
					<xsl:when test="titre">
						<xsl:value-of select="titre"/>
					</xsl:when>
					<xsl:when test="count(notebio) = 1">Note biographique</xsl:when>
					<xsl:otherwise>Notes biographiques</xsl:otherwise>
			</xsl:choose>
		</xsl:if>
		<xsl:if test="self::grnote">
			<xsl:choose>
				<xsl:when test="titre">
					<xsl:value-of select="titre"/>
				</xsl:when>
				<xsl:when test="count(note) = 1">Note</xsl:when>
				<xsl:otherwise>Notes</xsl:otherwise>
			</xsl:choose>
		</xsl:if>
		<xsl:if test="self::merci">
		<xsl:choose>
			<xsl:when test="titre">
				<xsl:value-of select="titre"/>
			</xsl:when>
			<xsl:otherwise>Remerciements</xsl:otherwise>
		</xsl:choose>
		</xsl:if>
		<xsl:if test="self::grbiblio">
			<xsl:choose>
				<xsl:when test="count(biblio) = 1">Bibliographie</xsl:when>
				<xsl:otherwise>Bibliographies</xsl:otherwise>
			</xsl:choose>
		</xsl:if>
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

</xsl:stylesheet>
