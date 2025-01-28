#ifndef WAVHIST_H
#define WAVHIST_H

#include <iostream>
#include <vector>
#include <map>
#include <sndfile.hh>

class WAVHist {
  private:
	std::vector<std::map<short, size_t>> counts;
	std::map<short, size_t> avg;
	std::map<short, size_t> diff;

  public:
	WAVHist(const SndfileHandle& sfh) {
		counts.resize(sfh.channels());
	}

	void update(const std::vector<short>& samples) {
		size_t n { };
		for(auto s : samples)
			counts[n++ % counts.size()][s]++;
	}

	void dump(const size_t channel) const {
		for(auto [value, counter] : counts[channel])
			std::cout << value << '\t' << counter << '\n';
	}
	
	void average(const std::vector<short>& samples){
		size_t mono = 0;
		std::vector<short> monoSampleAvg;
		//std::map<short, size_t> avg;
		for(size_t i = 0; i < samples.size(); i=i+2){
			// std::cout<<"L:\t";
			// std::cout<< samples[i];
			// std::cout<<"\n";
			// std::cout<<"R:\t";
			// std::cout<< samples[i+1];
			// std::cout<<"\n";
			// std::cout<<"Mono:\t";
			mono = (samples[i] + samples[i+1])/2;
			//std::cout<<mono;
			//std::cout<<"\n";
			monoSampleAvg.push_back(mono);
			avg[mono]++;
		}
		
	}
	
	void dumpAvg(){
		for(auto [value, counter] : avg){
			std::cout << value << '\t' << counter << '\n';
		}
	}

	//TESTAR
	void difference(const std::vector<short>& samples){
		size_t mono = 0;
		std::vector<short> monoSampleDiff;
		//std::map<short, size_t> avg;
		for(size_t i = 0; i < samples.size(); i=i+2){
			mono = (samples[i] - samples[i+1])/2;;
			monoSampleDiff.push_back(mono);
			diff[mono]++;
		}
		// //Calcular histograma
		// for(size_t i = 0; i < monoSampleDiff.size(); i++){
		// 	short sample = monoSampleDiff[i];
		// 	if (diff.count(sample) == 0){ //ainda nao tem este valor no histograma
		// 		int counter = 1;
		// 		for(size_t j = i+1; j < monoSampleDiff.size(); j++){
		// 			if (sample == monoSampleDiff[j]){
		// 				counter = counter + 1;
		// 			}
		// 		}
		// 		diff.insert({sample,counter});
		// 	}
		// }
	}

	void dumpDifference(){
		for(auto [value, counter] : diff){
			std::cout << value << '\t' << counter << '\n';
		}
	}
};

#endif

