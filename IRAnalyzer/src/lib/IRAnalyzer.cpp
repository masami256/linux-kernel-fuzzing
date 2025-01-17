#include "IRAnalyzer.h"

using namespace llvm;

cl::list<std::string> InputFilenames(
    cl::Positional, cl::OneOrMore, cl::desc("<input bitcode files>"));

cl::opt<bool> BBAnalyze(
    "bb-analyze", 
	cl::desc("Basic Block analyze"), 
	cl::NotHidden, cl::init(false));

static void countBasicBlocks(llvm::Module &M, std::vector<std::string> &data) {
	
	std::string moduleName = M.getName().str();
	char modulePath[PATH_MAX] = { 0 };
	realpath(moduleName.c_str(), modulePath);

	for (auto &F : M) {
		if (F.getName().str().find("llvm.") == 0) {
			continue;
		}
		unsigned totalBlocks = F.size();

		std::stringstream ss;
		ss << "[" 
			<< '"'
			<< modulePath 
			<< '"'
			<< "," 
			<< '"'
			<< F.getName().str() 
			<< '"'
			<< "," 
			<< totalBlocks 
			<< "]\n";
		data.push_back(ss.str());
	}
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

	for (auto &data : AllData) {
		std::cout << data;
	}
}

int main(int argc, char **argv)
{
    cl::ParseCommandLineOptions(argc, argv, "global analysis\n");
    std::cout << "Total " << InputFilenames.size() << " file(s)\n";

    run(InputFilenames);
}