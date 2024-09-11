#include <iostream>
#include <filesystem>
#include <sndfile.h>
#include <samplerate.h>

namespace fs = std::filesystem;

void processAudioFile(const fs::path& filePath) {
    SF_INFO sfInfo;
    sfInfo.format = 0;
    SNDFILE* inFile = sf_open(filePath.string().c_str(), SFM_READ, &sfInfo);
    if (!inFile) {
        std::cerr << "Error reading file: " << filePath << std::endl;
        return;
    }

    if (sfInfo.channels != 1) {
        std::cerr << "Only mono audio files are supported: " << filePath << std::endl;
        sf_close(inFile);
        return;
    }

    int targetSampleRate = 44100;
    std::vector<float> input(sfInfo.frames);
    sf_readf_float(inFile, input.data(), sfInfo.frames);
    sf_close(inFile);

    double ratio = static_cast<double>(targetSampleRate) / sfInfo.samplerate;
    std::vector<float> output(static_cast<size_t>(input.size() * ratio));
    SRC_DATA srcData;
    srcData.data_in = input.data();
    srcData.input_frames = sfInfo.frames;
    srcData.data_out = output.data();
    srcData.output_frames = output.size();
    srcData.src_ratio = ratio;

    int error = src_simple(&srcData, SRC_SINC_BEST_QUALITY, sfInfo.channels);
    if (error) {
        std::cerr << "Error during resampling: " << src_strerror(error) << std::endl;
        return;
    }

    SF_INFO outSfInfo = sfInfo;
    outSfInfo.samplerate = targetSampleRate;
    outSfInfo.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16;
    std::string outFile = filePath.stem().string() + "_resampled.wav";
    SNDFILE* outFileHandle = sf_open(outFile.c_str(), SFM_WRITE, &outSfInfo);
    if (!outFileHandle) {
        std::cerr << "Error creating output file: " << outFile << std::endl;
        return;
    }

    sf_writef_float(outFileHandle, output.data(), srcData.output_frames_gen);
    sf_close(outFileHandle);
}

int main() {
    std::string folderPath = "path_to_your_audio_files";

    for (const auto& entry : fs::directory_iterator(folderPath)) {
        if (entry.is_regular_file()) {
            processAudioFile(entry.path());
        }
    }

    return 0;
}