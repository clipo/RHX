#ifndef SQEXT_H
#define SQEXT_H

#include <sqlite3.h>

#ifdef _cplusplus
extern "C" {
#endif

int		sqlitex_registerFunctions(sqlite3 * dbh);

#ifdef _cplusplus
}
#endif

#endif
