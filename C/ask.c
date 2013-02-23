#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 8192

/* Generate a single question from the provided text string */
char *generateQn(char *article) {
    /* Make GCC happy */
    article = article;

    return "Is this a placeholder question?";
}

/* Read an article into a string */
char *readArticleFile(char *filePath) {
    FILE *file = fopen(filePath, "r");
    if (!file) {
        printf("Error opening file: %s\n", filePath);
        exit(1);
    }

    char *article = (char *)malloc(MAX_LINE);
    char *buffer = (char *)malloc(MAX_LINE);
    while ((buffer = fgets(buffer, MAX_LINE, file)) != NULL) {
        sprintf(article, "%s%s", article, buffer);
    }

    free(buffer);
    return article;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        printf("Usage: ./ask article.txt nquestions\n");
        exit(1);
    }

    char *filePath = argv[1];
    int nqns = atoi(argv[2]);

    char *article = readArticleFile(filePath);

    for (int i = 0; i < nqns; i++) {
        char *qn = generateQn(article);
        printf("Q%d from %s: \"%s\"\n", i+1, filePath, qn);
    }
    
    fflush(stdout);  /* Make sure printf works */

    return 0;
}