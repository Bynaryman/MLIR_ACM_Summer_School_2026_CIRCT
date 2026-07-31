#include "Tutorial/Passes.h"

namespace tutorial {

void registerFuncToHWModulePass();
void registerLowerE4M3FNToCombPass();

void registerPasses() {
  registerFuncToHWModulePass();
  registerLowerE4M3FNToCombPass();
}

} // namespace tutorial
