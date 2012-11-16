#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include <sqlite3.h>
#include <sqext.h>

static sqlite3 *	openDatabase(char * dbname)
{
	static int		dbmode = 0;
	sqlite3 *	dbh;
	char *		errmsg;
	
	dbh = sqlite3_open(dbname, dbmode);
	if (dbh == NULL)
	{
		fprintf(stderr, "Unable to open database: %s\n", errmsg);
		sqlite3_freemem(errmsg);
		return NULL;
	}
	return dbh;
}

static void closeDatabase(sqlite3 * dbh)
{
	if (dbh != NULL)
		sqlite3_close(dbh);
}

static void	showUsage(char * appName)
{
	static const char * usage[] =
	{
		"Usage: %s [options]",
		"Options:",
		"\t-db database-name -- specify database name - default = exp1.db",
		"\t-i script-name -- specify input script name - default = exp1.script",
		"\t-h -- show this message",
		NULL
	};
}
static char *	getNextArg(int * argcp, char *** argvp, char * dflt)
{
	if (--*argcp <= 0)
		return dflt;
	return *++*argvp;
}
static int exec_callback(void *pArg, int argc, char **argv, char **columnNames)
{
	int		i;
	for (i = 0; i < argc; i++)
	{
		printf("%s%c", argv[i], i == argc - 1 ? '\n' : '|');
	}
	return SQLITE_OK;
}
static int		readScript(char * scriptname, sqlite3 * dbh)
{
	FILE *	f = fopen(scriptname, "r");
	char	line[500];
	char	sql[2000];
	char *	errmsg;
	long	repeat = 1;
	long	i;

	if (f == NULL)
	{
		fprintf(stderr, "%s: can't open\n", scriptname);
		return -1;
	}

	sql[0] = 0;
	while (fgets(line, sizeof(line), f) != NULL)
	{
		if (strncmp(line, "--", 2) == 0)
		{
			printf("%s", line);
			continue;
		}
		else if (strncmp(line, "!repeat", 7) == 0)
		{
			printf("%s", line);
			repeat = atol(line + 8);
			sqlite_exec(dbh, "begin transaction;", NULL, NULL, &errmsg);
			continue;
		}
		else if (strncmp(line, "!endrepeat", 10) == 0)
		{
			printf("%s", line);
			repeat = 1;
			sqlite_exec(dbh, "commit transaction;", NULL, NULL, &errmsg);
			continue;
		}
		strcat(sql, line);
		if (sqlite_complete(sql))
		{
			printf("script> %s", sql);
			for (i = 0; i < repeat; i++)
			{
				if (sqlite_exec(dbh, sql, exec_callback, NULL, &errmsg) != SQLITE_OK)
				{
					printf("Error: %s\n", errmsg);
					sqlite_freemem(errmsg);
				}
			}
			sql[0] = 0;
		}
	}

	fclose(f);
	return 0;
}
static void	showBanner(char * appname, char * dbname, char * scriptname)
{
	printf("%s -db %s -i %s\n", appname, dbname, scriptname);
}

int	main(int argc, char ** argv)
{
	sqlite3 *	dbh;
	char *		dbname = "exp1.db";
	char *		scriptname = "exp1.script";
	char *		appName = argv[0];

	while (--argc > 0)
	{
		if (strcmp(*++argv, "-db") == 0)
		{
			dbname = getNextArg(&argc, &argv, dbname);
		}
		else if (strcmp(*argv, "-i") == 0)
		{
			scriptname = getNextArg(&argc, &argv, scriptname);
		}
		else if (strcmp(*argv, "-h") == 0)
		{
			showUsage(appName);
			exit(0);
		}
	}

	showBanner(appName, dbname, scriptname);
	
	if ((dbh = openDatabase(dbname)) == NULL)
		exit(1);

	sqlitex_registerFunctions(dbh);

	readScript(scriptname, dbh);
	closeDatabase(dbh);
}
