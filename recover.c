#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define BLOCK_SIZE 512
int main(int argc, char *argv[])
{
    // check if the user typed the name of the file to be recovered as a command line argument
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }
    // open the file the user wan to recover
    FILE *input = fopen(argv[1], "r");
    // if the file is empty print that to the user
    if (input == NULL)
    {
        printf("Could not open the infile\n");
        return 2;
    }
    // declare the block as 512 bytes and set a counter to zero
    typedef uint8_t BYTE;
    BYTE block[BLOCK_SIZE];
    int counter = 0;
    // allocate enough space to write the file name of 3 integers ### every int takes 4 bytes so we give it 12 bytes (12 chars)
    char filename[12];
    // make a new file for the putput image 
    FILE *img = NULL;
    
    while (true)
    {
        // read a block of memomry from input file
        size_t bytes_read = fread(block, BLOCK_SIZE, 1, input);
        // break out of loop when reach the end of the input file
        if (bytes_read == 0 && feof(input))
        {
            break;
        }
        //check to see if the first four bytes of the block represents a JPEG file
        bool containsJpegHeader = block[0] == 0xff && block[1] == 0xd8 && block[2] == 0xff && (block[3] & 0xf0) == 0xe0;
        
        // if found another JPEG, we must close the previous file
        if (containsJpegHeader && img != NULL)
        {
            fclose(img);
            counter ++;
        }
        // if we found a JPEG, we need to open the file for writing
        if (containsJpegHeader)
        {
            sprintf(filename, "%03i.jpg", counter);
            img = fopen(filename, "w");
        }
        // when we have an open file, write to that file
        if (img != NULL)
        {
            fwrite(block, BLOCK_SIZE, bytes_read, img);
        }
    }
    // close last jpeg file
    fclose(img);

    // close infile
    fclose(input);

    // success
    return 0;
}
