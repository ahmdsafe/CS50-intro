/************************************************************************
*                            readability                                *
* assessing the readability level of a text by using Coleman-Liau index *
***************************by/ Ahmed Saif*******************************/

#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

//variables for counting letters, words & sentences
int counterL = 0;
int counterW = 1;
int counterS = 0;

//function prototypes
int count_letters(string text);
int count_words(string text);
int count_sentences(string text);

// getting the text from user, calculating and printing the index
int main(void)
{
    // getting the text from user
    string text = get_string("text: ");  
    // getting value of counters from functions
    int L = count_letters(text);
    int W = count_words(text);
    int S = count_sentences(text);  
    //calculating the index
    float index = 0.0588 * (L * 100 / W) - 0.296 * (S * 100 / W) - 15.8;
    index = round(index);
    //showing final result
    if (index >= 16)
    {
        printf("Grade 16+\n") ;
    }
    else if (index < 1)
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("Grade %i\n", (int)index);
    }
 }

//function for counting letters
int count_letters(string text)
{
  for (int i=0, n = strlen(text); i < n; i++)
    {
        if (isalpha(text[i]))
        {
            counterL++;
        }
    }
 return (int)counterL;
}

//function for counting words
int count_words(string text)
{
  for (int i=0, n = strlen(text); i < n; i++)
    {
        if (isblank(text[i]))
        {
            counterW++;
        }
    }
 return (int)counterW;
}

//function for counting sentences
int count_sentences(string text)
{
    for (int i=0, n = strlen(text); i < n; i++)
    {
        if (text[i] == '.' || text[i]=='!' || text[i]=='?')
        {
            counterS++;
        }
    }
 return (int)counterS;
}
