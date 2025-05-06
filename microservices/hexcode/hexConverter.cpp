#include <string>
#include <iostream>
#include <sstream>
#include <vector>

// -------------------------------------------------------
//  convert an rgb hexcode to a matching color's name
//      input: hexcode as a string
//      output: color name as a string
// -------------------------------------------------------
std::string hex_to_string(const std::string hexcode){

    // copy the hex string and create a vector of chars
    std::string str = hexcode;
    std::vector<char> chars;

    // push the string to the vector one char at a time
    for(char c : str){
        chars.push_back(c);
    }

    // check for a hashtag symbol (#) preceeding the hex
    // remove it if found
    // if(chars.front() == '#'){
    //     chars.erase(chars.begin());
    // }

    int r, int g, int b;

    char sixteens_place, char ones_place;

    ones_place = chars.pop_back();
    sixteens_place = chars.pop_back();

    // compare using ASCII values
    if(ones_place >= 'A'){
        b == 
    }
    
    

}
