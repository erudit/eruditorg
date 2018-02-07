from lxml import etree as et


def test_can_determine_if_an_article_publication_is_allowed():
    from erudit.management.commands.import_journals_from_fedora import Command
    command = Command()

    issue_article_node = et.fromstring('<article horstheme="oui" idproprio="84958ac" lang="fr" ordseq="33" qualtraitement="minimal" typeart="compterendu"><urlpdf taille="2,9" unite="mo">/culture/images1058019/images02973/84958ac.pdf</urlpdf><pagination><ppage>64</ppage><dpage>64</dpage></pagination><notegen lang="fr" porteenoteg="numero" typenoteg="edito"><alinea>Un DVD est disponible sur abonnement papier</alinea></notegen><liminaire><grtitre><surtitre>Points de vue</surtitre><surtitre2>Vidéothèque interdite</surtitre2><trefbiblio><marquage typemarq="italique">The World, the Flesh and the Devil</marquage> (1959) de Ranald MacDougall</trefbiblio></grtitre><grauteur><auteur id="au1"><nompers><prenom>Apolline</prenom><nomfamille>Caron-Ottavi</nomfamille></nompers></auteur></grauteur></liminaire></article>')  # noqa
    assert command._get_is_publication_allowed(issue_article_node)

    issue_article_node_accessible_non = et.fromstring('<article horstheme="oui" idproprio="84959ac" lang="fr" ordseq="34" qualtraitement="minimal" typeart="autre">\n  <accessible>non</accessible>\n  <notegen lang="fr" porteenoteg="numero" typenoteg="edito">\n    <alinea>Un DVD est disponible sur abonnement papier</alinea>\n  </notegen>\n<liminaire>\n <grtitre>\n  <surtitre>DVD 24 images</surtitre>\n                  <titre>Stars et mutants&#160;: 7 courts qu&#233;b&#233;cois</titre>\n                \n         </grtitre>\n</liminaire>\n</article>\n')  # noqa
    assert not command._get_is_publication_allowed(issue_article_node_accessible_non)
