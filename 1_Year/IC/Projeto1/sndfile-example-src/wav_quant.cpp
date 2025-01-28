#include <iostream>
#include <vector>
#include <sndfile.hh>
#include "wav_quant.h"

using namespace std;

constexpr size_t FRAMES_BUFFER_SIZE = 65536; // Buffer for reading/writing frames

int main(int argc, char *argv[]) {
    SndfileHandle sfhIn { argv[argc-1] };
	if(sfhIn.error()) {
		cerr << "Error: invalid input file\n";
		return 1;
    }

    cout << '\t' << sfhIn.frames() << " frames\n";

}