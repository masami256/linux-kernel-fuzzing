
#include "IRDumper.h"

using namespace llvm;

void saveModule(Module &M, Twine filename)
{
    int bc_fd;
    StringRef FN = filename.getSingleStringRef();
    sys::fs::openFileForWrite(FN.take_front(FN.size() - 2) + ".bc", bc_fd);
    raw_fd_ostream bc_file(bc_fd, true, true);
    WriteBitcodeToFile(M, bc_file);
}

struct IRDumperPass : public PassInfoMixin<IRDumperPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
		std::cout << "IRDumperPass in function: " << M.getName().str() << std::endl;
        saveModule(M, M.getName());
        return PreservedAnalyses::all();
    }
};

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo()
{
    return {.APIVersion = LLVM_PLUGIN_API_VERSION,
            .PluginName = "IRDumper",
            .PluginVersion = LLVM_VERSION_STRING,
            .RegisterPassBuilderCallbacks = [](PassBuilder& PB) {
                PB.registerOptimizerEarlyEPCallback(
                    [](ModulePassManager& PM, OptimizationLevel /* Level */) {
                        PM.addPass(IRDumperPass{});
                    });
            }};
}
