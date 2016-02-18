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
		<section id="meta" class="meta">
			<div class="row">
				<div class="col-md-8">
					<div class="grtitre">
						<h1>
							<xsl:if test="liminaire/grtitre/titre">
								<xsl:apply-templates select="liminaire/grtitre/titre"/>
							</xsl:if>
							<xsl:if test="liminaire/grtitre/sstitre">
								<xsl:apply-templates select="liminaire/grtitre/sstitre"/>
							</xsl:if>
							<xsl:if test="liminaire/grtitre/trefbiblio">
								<xsl:apply-templates select="liminaire/grtitre/trefbiblio"/>
							</xsl:if>
						</h1>
					</div>
				</div>
				<div class="col-md-4">
					<div class="coverpage">
						<img src="todo" alt="Couverture du numéro" class="img-responsive"/>
					</div>
				</div>
				<div class="row">
					<div class="col-md-6">
						<div class="infoarticle">
							<div class="grcontributeur">
								<xsl:apply-templates select="liminaire/grauteur/auteur"/>
							</div>
							<div class="idpublic">
								<div class="uri">
									URI&#160;
									<a href="{$uriStart}{$iderudit}">
										<xsl:value-of select="$uriStart"/>
										<xsl:value-of select="$iderudit"/>
									</a>
								</div>
								<div class="doi">
									DOI&#160;
									<a href="{$doiStart}10.7202/{$iderudit}">
										10.7202/<xsl:value-of select="$iderudit"/>
									</a>
								</div>
							</div>
						</div>
					</div>
					<div class="col-md-6">
						<div class="refpapier">
							<div>
								<xsl:apply-templates select="../article/@typeart"/> de la revue
							</div>
							<div>
								<a href="{$urlSavant}{$titreAbrege}">
									<xsl:value-of select="admin/revue/titrerev"/>
								</a>
							</div>
							<div>
								<xsl:value-of select="admin/numero/grtheme/theme"/>
							</div>
							<div>
								<xsl:apply-templates select="admin/numero" mode="refpapier"/>
							</div>
							<xsl:apply-templates select="admin/droitsauteur"/>
						</div>
					</div>
				</div>
			</div>
		</section>
		<hr/>

		<!--=== plan de l'article ===-->
		<div class="row">
			<xsl:if test="//corps">
				<div class="col-md-3">
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
				</div>
			</xsl:if>
			<div class="col-md-6 col-md-offset-1">
				<xsl:apply-templates select="//resume"/>
			</div>
		</div>

		<!-- ********* Corps ******** -->
		<xsl:apply-templates select="corps"/>

	</xsl:template>

	<!--=========== TEMPLATES ===========-->

	<!--====== CORPS ======-->
	<xsl:template match="corps">
		<div class="row">
			<div class="col-md-6 col-md-offset-4">
				<section class="{name()}">
					TODO
				</section>
				<hr/>
			</div>
		</div>
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
		<div class="contributeur">
			<xsl:apply-templates select="*" mode="lim"/>
		</div>
	</xsl:template>
	<xsl:template match="auteur">
		<div class="{name()}">
			<xsl:value-of select="."/>
		</div>
	</xsl:template>

	<xsl:template match="auteur/nompers" mode="lim">
		<xsl:if test="child::node()/child::text()">
			<div class="{name()}">
				<xsl:call-template name="element_nompers_affichage">
					<xsl:with-param name="nompers" select="."/>
				</xsl:call-template>
			</div>
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
		<div class="affiliation">
			<xsl:apply-templates select="fonction"/>
			<xsl:apply-templates select="divorg"/>
			<xsl:apply-templates select="nomorg"/>
			<xsl:apply-templates select="adresse"/>
			<xsl:apply-templates select="alinea"/>
		</div>
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
		<div class="volumaison">
			<xsl:for-each select="volume | nonumero[1] | pub/periode | pub/annee | pagination">
				<xsl:apply-templates select="."/>
				<xsl:if test="position() != last()">
					<xsl:text>, </xsl:text>
				</xsl:if>
			</xsl:for-each>
		</div>
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
      <div class="{name()}">
        <xsl:apply-templates/>
      </div>
    </xsl:template>

	<!-- resume -->
	<xsl:template match="//resume">
		<div id="{name()}" class="{name()}">
			<xsl:if test="@lang='fr'">
				<h2>Résumé</h2>
				<xsl:apply-templates/>
				<xsl:if test="//grmotcle[@lang='fr']/motcle">
					<div class="motcle">
						<span class="etiquette">Mots clés : </span>
						<xsl:for-each select="//grmotcle[@lang='fr']/motcle">
							<xsl:apply-templates/>
							<xsl:if test="position() != last()">
								<xsl:text>, </xsl:text>
							</xsl:if>
						</xsl:for-each>
					</div>
				</xsl:if>
			</xsl:if>
			<xsl:if test="@lang='en'">
			<h2>Abstract</h2>
				<xsl:apply-templates select="//grtitre/grtitreparal/titreparal[@lang='en']" mode="lim"/>
				<xsl:apply-templates select="alinea"/>
				<xsl:if test="//grmotcle[@lang='en']/motcle">
					<div class="motcle">
					<span class="etiquette">Keywords : </span>
					<xsl:for-each select="//grmotcle[@lang='en']/motcle">
						<xsl:apply-templates/>
						<xsl:if test="position() != last()">
							<xsl:text>, </xsl:text>
						</xsl:if>
					</xsl:for-each>
					</div>
				</xsl:if>
			</xsl:if>
			<xsl:if test="@lang='es'">
				<h2>Resumen</h2>
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

</xsl:stylesheet>
