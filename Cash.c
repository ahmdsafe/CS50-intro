/***********************************************************************************
*                                    Cash                                          *
* implementing a program to count the least number of coins can be used for change *
*********************************by/ Ahmed Saif************************************/

#include <stdio.h>
#include <cs50.h>
#include <math.h>

int main(void)
{
    float change;
    //for accepting only positive values
    do
    {
        change = get_float("change: ");  
    }
    while (change < 0);
    //variables to be used later
    int quarters = 25;
    int dimes = 10;
    int nickles = 5;
    int pinnies = 1;
    
    //for converting dollars to cents 
    int cents = round(change * 100); 
    //counting number of coins needed
    int number = 0;
    //counting number of quarters
    while (cents >= quarters)
    {
        cents = cents - quarters;
        number++;
    }
    //counting number of dimes   
    while (cents >= dimes)
    {
        cents = cents - dimes;
        number++;
    }
    //counting number of nickles
    while (cents >= nickles)
    {
        cents = cents - nickles;
        number++;
    }
    //counting number of pinnies
    while (cents >= pinnies)
    {
        cents = cents - pinnies;
        number++;
    }
    //printing total number of coins needed
    printf("%i \n ", number);   
}
