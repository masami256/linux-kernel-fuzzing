#include "IRAnalyzer.h"

using namespace llvm;

cl::list<std::string> InputFilenames(
    cl::Positional, cl::OneOrMore, cl::desc("<input bitcode files>"));


cl::opt<std::string> OutputFilename(
    "output", cl::desc("output file name"),
    cl::init("bb_info.json"));

cl::opt<bool> BBAnalyze(
    "bb-analyze", 
	cl::desc("Basic Block analyze"), 
	cl::NotHidden, cl::init(false));

static void countBasicBlocks(llvm::Module &M, std::vector<std::string> &data) {
	
	std::string moduleName = M.getName().str();
	char modulePath[PATH_MAX] = { 0 };
	realpath(moduleName.c_str(), modulePath);
	std::vector<std::string> tmp;

	for (auto &F : M) {
		if (F.getName().str().find("llvm.") == 0) {
			continue;
		}

		if (F.size() == 0) {
			// Skip functions without basic blocks
			continue;
		}

		std::stringstream ss;
		ss << '"'
			<< F.getName().str() 
			<< "\": {" 
			<< "\"BasicBlocks\":"
			<< F.size() 
			<< "}";
		tmp.push_back(ss.str());
	}

	std::stringstream s;
	s << "\"" << modulePath << "\": {";
	data.push_back(s.str());
	for (auto i = 0; i < tmp.size(); ++i) {
		data.push_back(tmp[i]);
		if (i < tmp.size() - 1) {
			data.push_back(",\n");
		}
	}
	data.push_back("\n}");
	data.push_back(",\n");
}

static void Write2Json(std::vector<std::string> AllData) {
	std::ofstream os(OutputFilename);
	if (!os) {
        std::cerr << "Failed to open file for writing.\n";
        return;
    }

    os << "{\n";
    bool firstPair = true; // Used to handle commas between JSON objects

	for (auto i = 0; i < AllData.size(); ++i) {
		std::string line = AllData[i];

		os << line;
	}
    os << "\n}\n"; // Close the JSON array
}

static void run(const cl::list<std::string> &InputFilenames)
{
    SMDiagnostic Err;
	std::vector<std::string> AllData;

	for (unsigned i = 0; i < InputFilenames.size(); ++i) {

		LLVMContext *LLVMCtx = new LLVMContext();
		std::unique_ptr<Module> M = parseIRFile(InputFilenames[i], Err, *LLVMCtx);

		if (M == NULL) {
			std::cout << InputFilenames[i] << ": error loading file '"
				<< InputFilenames[i] << "'\n";
			continue;
		}

		countBasicBlocks(*M, AllData);	
	}

	AllData.pop_back();

	Write2Json(AllData);
	std::cout << "Output file: " << OutputFilename << "\n";
}

int main(int argc, char **argv)
{
    cl::ParseCommandLineOptions(argc, argv, "global analysis\n");
    std::cout << "Total " << InputFilenames.size() << " file(s)\n";

    run(InputFilenames);
}