#include <iostream>

#include <fstream>
#include <iostream>
#include <math.h>
#include <vector>
#include <random>
#include <chrono>
#include <time.h>
#include <sstream>
#include <string>

#include <iomanip>
#include <assert.h>
#include <execinfo.h>

#include <boost/unordered_map.hpp>
#include <boost/foreach.hpp>

typedef boost::unordered_map<std::string, double> map;

std::vector<std::string> &split(const std::string &s, char delim, std::vector<std::string> &elems) {
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, delim)) {
    	if( !item.empty())
        	elems.push_back(item);
    }
    return elems;
}

void printVector(std::vector<std::string> vec)
{
	for(int i = 0; i < vec.size(); i++)
		std::cout << vec[i] << std::endl;
}

std::string getTableKey( std::string e_word, std::string f_word)
{
	return e_word + "-" + f_word;
}

void printPData(map t_e_f, std::vector < std::vector<std::string> > &foreign_set, std::vector< std::vector<std::string> > &english_set)
{

	double total_sum = 0.0;

	for( int i = 0; i < foreign_set.size(); i++ )
	{
		std::vector<std::string> f_sentence = foreign_set[i];
		std::vector<std::string> e_sentence = english_set[i];

		double prod = 1.0;

		for(int e_idx = 0; e_idx < e_sentence.size(); e_idx++)
		{
			double sum_val = 0.0;
			std::string e_word = e_sentence[e_idx];

			for(int f_idx =0; f_idx < f_sentence.size(); f_idx++)
			{
				std::string f_word = f_sentence[f_idx];
				sum_val += t_e_f[ getTableKey(e_word, f_word) ];
			}

			prod *= sum_val;
		}

		total_sum += log(prod);
	}

	printf("P(data) is %f \n", total_sum);

}

void loadFile( std::vector < std::vector<std::string> > &foreign_set, std::vector< std::vector<std::string> > &english_set, std::string filename)
{

	std::ifstream ifile(filename);

	std::string line;

	int count = 0;
	while (std::getline(ifile, line) )
	{

		int pos = line.find("|||");

		std::string foreign_sent = line.substr(0, pos);
		// std::cout << foreign_sent << std::endl;
		std::vector<std::string> foreign_vec; 
		split(foreign_sent, ' ', foreign_vec);
		// printVector(foreign_vec);

		std::string english_sent = line.substr(pos+3);
		// std::cout << english_sent << std::endl;
		std::vector<std::string> english_vec;
		split(english_sent, ' ', english_vec);
		// printVector(english_vec);

		// if( english_vec.size() > 15 || foreign_vec.size() > 15){
			count++;
			// continue;
		// }


		english_set.push_back(english_vec);
		foreign_set.push_back(foreign_vec);
		
		if(count > 10)
			break;

	}
	printf("Num Removed: %d \n", count);

}


std::string getKeyPart(std::string str, int pos)
{
	int idx = str.find('-');

	if( pos == 0 )
		return str.substr(0, idx);
	else
		return str.substr(idx+1);
}

std::string getAligmentForm(int f_idx, int e_idx)
{
	std::string key = std::to_string(f_idx) + "-" + std::to_string(e_idx);
	return key;
}


void IBM1( std::vector < std::vector<std::string> > foreign_set, std::vector< std::vector<std::string> > english_set )
{

	map t_e_f;

	// Initialize T Table
	for(int i = 0; i < foreign_set.size(); i++)
	{
		std::vector<std::string> foreign_sentence = foreign_set[i];
		std::vector<std::string> english_sentence = english_set[i];

		for(int f_idx = 0; f_idx < foreign_sentence.size(); f_idx++)
		{
			std::string f_word = foreign_sentence[f_idx];
			
			for (int e_idx = 0; e_idx < english_sentence.size(); e_idx++)
			{
				std::string e_word = english_sentence[e_idx];
				std::string key = getTableKey(e_word, f_word);
				//t_e_f[key] = 1.0 / foreign_sentence.size();
				t_e_f[key] = 1.0;
			}
		}
	}

	BOOST_FOREACH(map::value_type key_pair, t_e_f) {
		t_e_f[key_pair.first] = t_e_f[key_pair.first] / t_e_f.size();
	}


	printf("Here \n");

	int iterations = 5;
	for(int iter = 0; iter < iterations; iter++)
	{

		printf("Iteration %d \n", iter);

		map count_e_f;
		map total_f;

		BOOST_FOREACH(map::value_type key_pair, t_e_f) {
			count_e_f[key_pair.first] = 0.0;

			std::string f_word = getKeyPart(key_pair.first, 1);
			total_f[f_word] = 0.0;
		}

		for(int i = 0; i < foreign_set.size(); i++)
		{
			std::vector<std::string> foreign_sentence = foreign_set[i];
			std::vector<std::string> english_sentence = english_set[i];

			std::vector<double> s_total;

			// INITIALIZE NORMALIZATION S_TOTAL
			for (int e_idx = 0; e_idx < english_sentence.size(); e_idx++)
			{
				std::string e_word = english_sentence[e_idx];

				double sum = 0.0;
				for(int f_idx = 0; f_idx < foreign_sentence.size(); f_idx++)
				{
					std::string f_word = foreign_sentence[f_idx];
					std::string key = getTableKey(e_word, f_word);
					sum += t_e_f[key];
				}
				
				s_total.push_back(sum);
			}

			// INITIALIZE NORMALIZATION S_TOTAL
			for (int e_idx = 0; e_idx < english_sentence.size(); e_idx++)
			{
				std::string e_word = english_sentence[e_idx];
				
				for(int f_idx = 0; f_idx < foreign_sentence.size(); f_idx++)
				{
				
					std::string f_word = foreign_sentence[f_idx];

					std::string key = getTableKey(e_word, f_word);

					count_e_f[key] += t_e_f[key] / s_total[e_idx];
					total_f[f_word] += t_e_f[key] / s_total[e_idx];
				
				}
			}

		}

		BOOST_FOREACH(map::value_type key_pair, t_e_f) {
			std::string f_word = getKeyPart(key_pair.first, 1);
			t_e_f[key_pair.first] = count_e_f[key_pair.first] / total_f[f_word];
		}



		printPData(t_e_f, foreign_set, english_set);
	}

	std::ofstream ofile("ibm1_c.out");

	for(int i = 0; i < foreign_set.size(); i++)
	{
		std::vector<std::string> foreign_sentence = foreign_set[i];
		std::vector<std::string> english_sentence = english_set[i];

		// INITIALIZE NORMALIZATION S_TOTAL
		for (int e_idx = 0; e_idx < english_sentence.size(); e_idx++)
		{
			std::string e_word = english_sentence[e_idx];

			std::string best_alignment = "";
			double best_prob = 0.0;

			for(int f_idx = 0; f_idx < foreign_sentence.size(); f_idx++)
			{
				std::string f_word = foreign_sentence[f_idx];
				std::string key = getTableKey(e_word, f_word);

				if( t_e_f[key] > best_prob)
				{
					best_prob = t_e_f[key];
					best_alignment = getAligmentForm(f_idx, e_idx);
				}

				printf("t_e_f: %f \n", t_e_f[key]);
			}
			return;
			
			ofile << best_alignment;
			if( e_idx != english_sentence.size() -1)
				ofile << " ";
		}
		ofile << "\n";
	}

	ofile.close();


// for f_idx, f_sent in enumerate(f_set):
//     e_sent = e_set[f_idx]

//     for e_idx, e_word in enumerate(e_sent):
//         best_f_e = (-1, -1)
//         best_prob = 0.0
//         for f_idx, f_word in enumerate(f_sent):
//             if t_e_f[(e_word, f_word)] > best_prob:
//                 best_prob = t_e_f[(e_word, f_word)]
//                 best_f_e = (f_idx, e_idx)

//         f.write( str(best_f_e[0]) + "-" + str(best_f_e[1]))
//         if e_idx != len(e_sent) - 1:
//             f.write(" ")
//     f.write("\n")



}

int main(int argc, char * argv[])
{

	std::vector < std::vector<std::string> > foreign_set;
	std::vector< std::vector<std::string> > english_set;

	loadFile(foreign_set, english_set, "dev-test-train.de-en");


	IBM1(foreign_set, english_set);





}

