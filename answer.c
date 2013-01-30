#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 8192

/* Answer a given question */
char *answerQn(char *qn, char *article) {
    /* Make GCC happy */
    qn = qn;
    article = article;

    return "Yes, of course!";
}

/* Read an article into a string */
char *readArticleFile(char *filePath) {
    FILE *file = fopen(filePath, "r");
    if (!file) {
        printf("Error opening file: %s\n", filePath);
        exit(1);
    }

    char *text = (char *)malloc(MAX_LINE);
    char *buffer = (char *)malloc(MAX_LINE);
    while ((buffer = fgets(buffer, MAX_LINE, file)) != NULL) {
        sprintf(text, "%s%s", text, buffer);
    }

    free(buffer);
    printf("Article:\n\n%s\n\n--------\n\n", text);
    return text;
}

/*
 * Read a list of questions into an array of strings, which we return,
 * and assign the number of questions to nqns.
 */
char **readQnFile(char *filePath, int *nqns) {
    FILE *file = fopen(filePath, "r");
    if (!file) {
        printf("Error opening file: %s\n", filePath);
        exit(1);
    }

    char **qns = (char **)malloc(MAX_LINE);
    *nqns = 0;
    while (1) {
        char *qn = (char *)malloc(MAX_LINE);
        if ((qn = fgets(qn, MAX_LINE, file)) == NULL) {
            free(qn);
            break;
        }

        qn[strlen(qn)-1] = '\0';  /* Don't include the '\n' at the end */
        qns[(*nqns)++] = qn;
    }

    return qns;
}

/* Free memory from the array of questions */
void freeQns(char **qns, int n) {
    for (int i = 0; i < n; i++) {
        free(qns[i]);
    }

    free(qns);
}

int main(int argc, char **argv) {
    if (argc != 3) {
        printf("Usage: ./answer article.txt questions.txt\n");
        exit(1);
    }

    char *articleFilePath = argv[1];
    char *qnsFilePath = argv[2];

    char *article = readArticleFile(articleFilePath);

    int nqns;
    char **qns = readQnFile(qnsFilePath, &nqns);

    printf("Here are the answers to the %d questions about \"%s\":\n\n",
        nqns, articleFilePath);

    /*
     * Iterate through the array of questions, answer each and print
     * the resulting question and answer.
     */
    for (int i = 0; i < nqns; i++) {
        char *qn = qns[i];
        char *ans = answerQn(qn, article);
        printf("Q%d:\t\"%s\"\n", i+1, qn);
        printf("A%d:\t\"%s\"\n\n", i+1, ans);
    }

    fflush(stdout);  /* Make sure we print everything to stdout */
    freeQns(qns, nqns);  /* Clean up memory */ 

    return 0;
}