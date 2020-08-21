module.exports = {
  ci: {
    collect: {
      url: [
        "https://www.erudit.org/fr/",
        "https://www.erudit.org/fr/revues/?sorting=name",
        "https://www.erudit.org/fr/revues/?sorting=disciplines",
        "https://www.erudit.org/fr/revues/images/",
        "https://www.erudit.org/fr/revues/images/auteurs/",
        "https://www.erudit.org/fr/revues/images/2017-n182-images03064/",
        "https://www.erudit.org/fr/revues/images/2017-n182-images03064/85562ac/",
        "https://www.erudit.org/fr/revues/ae/",
        "https://www.erudit.org/fr/revues/ae/auteurs/",
        "https://www.erudit.org/fr/revues/ae/2017-v93-n4-ae04492/",
        "https://www.erudit.org/fr/revues/ae/2017-v93-n4-ae04492/1058591ar/",
        "https://www.erudit.org/fr/recherche/avancee/",
        "https://www.erudit.org/fr/recherche/?basic_search_term=environnement",
      ],
      settings: {
        chromeFlags: "--no-sandbox --headless",
        onlyCategories: [
          "performance",
          "accessibility",
          "best-practices",
          "seo",
        ],
      },
      numberOfRuns: 3,
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};
