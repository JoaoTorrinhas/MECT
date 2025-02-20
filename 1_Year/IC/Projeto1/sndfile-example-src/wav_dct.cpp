#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <fftw3.h>
#include <sndfile.hh>
#include "BitStream.cpp"

using namespace std;

int main(int argc, char *argv[]) {

	bool verbose { false };
	size_t bs { 1024 };
	double dctFrac { 0.2 };

	if(argc < 3) {
		cerr << "Usage: wav_dct [ -v (verbose) ]\n";
		cerr << "               [ -bs blockSize (def 1024) ]\n";
		cerr << "               [ -frac dctFraction (def 0.2) ]\n";
		cerr << "               wavFileIn wavFileOut\n";
		return 1;
	}

	for(int n = 1 ; n < argc ; n++)
		if(string(argv[n]) == "-v") {
			verbose = true;
			break;
		}

	for(int n = 1 ; n < argc ; n++)
		if(string(argv[n]) == "-bs") {
			bs = atoi(argv[n+1]);
			break;
		}

	for(int n = 1 ; n < argc ; n++)
		if(string(argv[n]) == "-frac") {
			dctFrac = atof(argv[n+1]);
			break;
		}

	SndfileHandle sfhIn { argv[argc-2] };
	if(sfhIn.error()) {
		cerr << "Error: invalid input file\n";
		return 1;
    }

	if((sfhIn.format() & SF_FORMAT_TYPEMASK) != SF_FORMAT_WAV) {
		cerr << "Error: file is not in WAV format\n";
		return 1;
	}

	if((sfhIn.format() & SF_FORMAT_SUBMASK) != SF_FORMAT_PCM_16) {
		cerr << "Error: file is not in PCM_16 format\n";
		return 1;
	}

	SndfileHandle sfhOut { argv[argc-1], SFM_WRITE, sfhIn.format(),
	  sfhIn.channels(), sfhIn.samplerate() };
	if(sfhOut.error()) {
		cerr << "Error: invalid output file\n";
		return 1;
    }

	if(verbose) {
		cout << "Input file has:\n";
		cout << '\t' << sfhIn.frames() << " frames\n";
		cout << '\t' << sfhIn.samplerate() << " samples per second\n";
		cout << '\t' << sfhIn.channels() << " channels\n";
	}

	size_t nChannels { static_cast<size_t>(sfhIn.channels()) };
	size_t nFrames { static_cast<size_t>(sfhIn.frames()) };

	// Read all samples: c1 c2 ... cn c1 c2 ... cn ...
	// Note: A frame is a group c1 c2 ... cn
	vector<short> samples(nChannels * nFrames);
	sfhIn.readf(samples.data(), nFrames);

	size_t nBlocks { static_cast<size_t>(ceil(static_cast<double>(nFrames) / bs)) };

	// Do zero padding, if necessary
	samples.resize(nBlocks * bs * nChannels);

	// Vector for holding all DCT coefficients, channel by channel
	vector<vector<double>> x_dct(nChannels, vector<double>(nBlocks * bs));

	// Vector for holding DCT computations
	vector<double> x(bs);

	// Direct DCT
	fftw_plan plan_d = fftw_plan_r2r_1d(bs, x.data(), x.data(), FFTW_REDFT10, FFTW_ESTIMATE);
	for(size_t n = 0 ; n < nBlocks ; n++)
		for(size_t c = 0 ; c < nChannels ; c++) {
			for(size_t k = 0 ; k < bs ; k++)
				x[k] = samples[(n * bs + k) * nChannels + c];

			fftw_execute(plan_d);
			// Keep only "dctFrac" of the "low frequency" coefficients
			for(size_t k = 0 ; k < bs * dctFrac ; k++)
				x_dct[c][n * bs + k] = x[k] / (bs << 1);

		}

	//Escrever no ficheiro o valor que vem do DCT
	vector<double> values;
	vector<double> arrayWithValues;
    fstream file;
    file.open("dct_file.txt", ios_base::out);
    //vector<vector<double>>::iterator itr;
	int contador = 0;
    for(int i = 0; i < x_dct.size(); i++){
        values = x_dct[i];
        for (int j = 0; j < values.size(); j++){
			arrayWithValues.push_back(values[j]);
			//cout << "Contador->\n" << contador;
			if (contador == 1024){

				for (int k = 0; k < arrayWithValues.size(); k++){
					file<<arrayWithValues[k]<<endl;
				}

				BitStream inputfile("dct_file.txt", "r");	// input file -> dct_file.txt
				ofstream outputfile("dct_fileBin.txt", ios::out); // outputfile
				//../sndfile-example-bin/wav_dct sample.wav out.wav 
				vector<int> bits;
				bits = inputfile.readNbits(inputfile.getSize()*8);
				inputfile.close();

				for(int i = 0; i < bits.size(); i++){
					outputfile << bits[i];
				}
				
				contador = 0;
				file.open("dct_file.txt", std::ofstream::out | std::ofstream::trunc);//limpar o ficheiro
				arrayWithValues.clear();
				outputfile.close();
			}	
			contador++;	
		}
			//contador++;
            //file<<values[j]<<endl;
			//cout << "Valores->" << values[j];
    }
    file.close();
	//cout << "Contador->\n" << x_dct.size();

	//Fazer o decode do ficheiro bin para txt
	//Não tivemos tempo...

	//ifstream inputFileDecode("dct_fileBin.txt", ios::in);
	//ofstream outputfile("dct_fileInverse.txt", ios::out);

	// Inverse DCT
	fftw_plan plan_i = fftw_plan_r2r_1d(bs, x.data(), x.data(), FFTW_REDFT01, FFTW_ESTIMATE);
	for(size_t n = 0 ; n < nBlocks ; n++)
		for(size_t c = 0 ; c < nChannels ; c++) {
			for(size_t k = 0 ; k < bs ; k++)
				x[k] = x_dct[c][n * bs + k];

			fftw_execute(plan_i);
			for(size_t k = 0 ; k < bs ; k++)
				samples[(n * bs + k) * nChannels + c] = static_cast<short>(round(x[k]));

		}

	sfhOut.writef(samples.data(), sfhIn.frames());
	return 0;
}

