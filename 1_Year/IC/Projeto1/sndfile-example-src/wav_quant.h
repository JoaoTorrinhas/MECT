#ifndef WAVQUANT_H
#define WAVQUANT_H

#include <iostream>
#include <vector>
#include <map>
#include <sndfile.hh>

class WAVQuant {
  private:
	std::vector<std::map<short, size_t>> counts;
	std::map<short, size_t> avg;
	std::map<short, size_t> diff;

  public:
	WAVQuant(const SndfileHandle& sfh) {
		counts.resize(sfh.channels());
	}
};

#endif

