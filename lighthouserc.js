module.exports = {
  ci: {
    collect: {
      url: [
        "https://www.erudit.org/fr/",
        // TODO: Use staging environment instead of prod and add other URLs.
      ],
      settings: {
        onlyCategories: [
          "performance",
          "accessibility",
          "best-practices",
          "seo",
        ],
      },
    },
  },
};
