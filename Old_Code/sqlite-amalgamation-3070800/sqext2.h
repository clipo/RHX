#ifndef SQEXT_H
#define SQEXT_H

#include <sqlite.h>

#ifdef _cplusplus
extern "C" {
#endif

int		sqlitex_registerFunctions(sqlite * dbh);

#ifdef _cplusplus
}
#endif

#endif
