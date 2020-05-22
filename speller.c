/*********************************************************************************************
                                        **dictionary.c**
 * CS50 > Problem Set 5 > Speller
 * Implements a dictionary's functionality.
 * written by Ahmed Saif
 *********************************************************************************************/


#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>

#include "dictionary.h"



// Represents a node in a hash table
typedef struct node
{
    char *word;
    struct node *next;
} node;

// define variable for counting words
unsigned int word_counter = 0;


// Number of buckets in hash table
#define N 7000
node *table[N];

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    // returning the result of the hash function in a variable called index
    unsigned int index = 0;
    index = hash(word);
    
    //comparing every word in the text with words from dictionary regardless of lowercase or uppercase
    for (node *tmp = table[index]; tmp != NULL; tmp = tmp->next)
    {
        if (strcasecmp(tmp->word, word) == 0)
        {
            // if found we return true (not misspelled)
            return true;
        }   
    }
    // if not found we return fasle meaning that this word is not in dictionary &  it is misspelled
    return false;

}
// a simple hash function to Hashes word to a number add to sum mod by total
unsigned int hash(const char *word)
{
    // initialize index to 0
    int index = 0;

    // sum ascii values
    for (int i = 0; word[i] != '\0'; i++)
    {
        // converting to lower cases words   
        index += tolower(word[i]);
    }

    // mod by size to stay w/in bound of table
    return index % N;

}



// Loads dictionary into memory, returning true if successful else false

bool load(const char *dictionary)
{
    char word[LENGTH + 1];
   
    //open the file of the dictionary as read only
    FILE *file = fopen(dictionary, "r");
    
    // if the file empty so no file to load & the function should return false
    if (file == NULL)
    {
        return false;
    }
    //start reading into file word by word & store it in a variable called word untill the EOF (end of file)
    while (fscanf(file, "%s\n", word) != EOF)
    {
        // create a space for a new node to hold the words we are reading and pointer to the next node
        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            return false;
        }
        n->word = malloc(strlen(word) + 1);
        strcpy(n->word, word);
        
        //send the word to the hash function to get back its index in the table
        int index = hash(word);
        
        //if there is nothing yet in that index put that node as the first one and point to nothing
        if (table[index] == NULL)
        {
            table[index] = n;
            n->next = NULL;
        }
        
        //else make the new node the head of the list & point to the first node in that index which in turn points to the next ...
        else
        {
            n->next = table[index];
            table[index] = n;
        }
        
        //increase the counter by one for each word found
        word_counter++;
    }
    
    // done reading and copying data, now we close the file back
    fclose(file);
    return true;
}


// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    return word_counter;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    //freeing every space we allocated by malloc
    for (int i = 0; i < N; i++)
    {
        // creating a cursor goes with the list one by one in each index
        node *cursor = table[i];
        while (cursor != NULL)
        {
            // creating a tmp that goes one step behind the cursor and freeing every node
            node *tmp = cursor;
            cursor = cursor->next;
            free(tmp);
        }
        return true;
    }
    return false;
}
