#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include <time.h>
#include <sys/types.h>
#include <sys/timeb.h>
#include <math.h>
#include <sqext.h>

#  define SQEXT_FUNC	static void

typedef void (*sqlFuncPtr)(sqlite3_context*,int,const char**);
typedef void (*sqlFinalizePtr)(sqlite3_context *);

typedef struct tm * (*TimeFunc)(const time_t *timer);

SQEXT_FUNC sqlitex_now(sqlite3_context * context,int argc,const char** argv)
{
	time_t			ret;
	time(&ret);
	sqlite3_set_result_int(context, ret);
	return;
}

static void sqlitex_formatTime(sqlite3_context * context,int argc,const char** argv, TimeFunc f, const char * dfltFormat)
{
	// argv[0] = a time as given by sqlitex_now()
	// argv[1] = NULL or a format string
	const char *	formatp = dfltFormat;
	time_t			timer;
	struct tm		gmt;
	char			ret[100];

	if (argc < 1 || argv[0] == NULL)
	{
		sqlite3_set_result_error(context, "formatTime requires 1 non-null numeric parameter", -1);
		return;
	}
	timer = atol(argv[0]);
	// is this really threadsafe? I don't think so. We should use
	// a mutex here.
	memcpy(&gmt, f(&timer), sizeof(gmt));

	if (argc >= 2 && strlen(argv[1]) > 0)
		formatp = argv[1];
	strftime(ret, sizeof(ret), formatp, &gmt);
	sqlite3_set_result_string(context, ret, -1);
}

SQEXT_FUNC sqlitex_formatGMTime(sqlite3_context * context,int argc,const char** argv)
{
	static const char *	format = "%Y/%m/%dT%H:%M:%SZ";
	sqlitex_formatTime(context, argc, argv, gmtime, format);
}
SQEXT_FUNC sqlitex_formatLocalTime(sqlite3_context * context,int argc,const char** argv)
{
	static const char *	format = "%Y/%m/%dT%H:%M:%S";
	sqlitex_formatTime(context, argc, argv, localtime, format);
}

SQEXT_FUNC	sqlitex_age(sqlite3_context * context,int argc,const char** argv)
{
	time_t	t0;
	time_t	t1;

	if (argc < 1 || argv[0] == NULL)
	{
		sqlite3_set_result_error(context, "age requires 1 non-null numeric parameter", -1);
		return;
	}
	t0 = atol(argv[0]);
	time(&t1);
	sqlite3_set_result_double(context, difftime(t1, t0));
}

SQEXT_FUNC	sqlitex_difftime(sqlite3_context * context,int argc,const char** argv)
{
	time_t	t1;
	time_t	t0;

	if (argc < 2 || argv[0] == NULL || argv[1] == NULL)
	{
		sqlite3_set_result_error(context, "difftime requires 2 non-null numeric parameters", -1);
		return;
	}
	t1 = atol(argv[0]);
	t0 = atol(argv[1]);
	sqlite3_set_result_double(context, difftime(t1, t0));
}

SQEXT_FUNC	sqlitex_distance(sqlite3_context * context,int argc,const char** argv)
{
	// expect x1, y1, x2, y2 all as doubles
	double	x1;
	double	y1;
	double	x2;
	double	y2;
	register double	xd;
	register double	yd;
	int		i;

	if (argc < 4)
	{
		sqlite3_set_result_error(context, "distance requires 4 parameters", -1);
		return;
	}
	for (i = 0; i < 4; i++)
	{
		if (argv[i] == NULL)
		{
			sqlite3_set_result_error(context, "distance requires 4 non-null numeric parameters", -1);
			return;
		}
	}
	
	x1 = atof(argv[0]);
	y1 = atof(argv[1]);
	x2 = atof(argv[2]);
	y2 = atof(argv[3]);
	xd = x1 - x2;
	yd = y1 - y2;
	sqlite3_set_result_double(context, sqrt(xd * xd + yd * yd));
}
typedef struct
{
	double	sumx;
	double	sumy;
	double	sumxsq;
	double	sumysq;
	double	sumxy;
	long	n;
} ParStats;

static double	psDispersionY(ParStats * p)
{
	return p->n * p->sumysq - p->sumy * p->sumy;
}
static double	psDispersionX(ParStats * p)
{
	return p->n * p->sumxsq - p->sumx * p->sumx;
}
static double	psDispersionXY(ParStats * p)
{
	return p->n * p->sumxy - p->sumx * p->sumy;
}

SQEXT_FUNC	sqlitex_collect1Stat(sqlite3_context * context,int argc,const char** argv)
{
	ParStats *	p;
	double		y;
	if (argc < 1) return;
	p = sqlite3_aggregate_context(context, sizeof(ParStats));
	if (p != NULL && argv[0] != NULL)
	{
		y = atof(argv[0]);
		p->n++;
		p->sumy += y;
		p->sumysq += y * y;
	}
}
SQEXT_FUNC	sqlitex_collect2Stats(sqlite3_context * context,int argc,const char** argv)
{
	ParStats *	p;
	double		y, x;
	if (argc < 2) return;
	p = sqlite3_aggregate_context(context, sizeof(ParStats));
	if (p != NULL && argv[0] != NULL && argv[1] != NULL)
	{
		p->n++;

		x = atof(argv[0]);
		p->sumx += x;
		p->sumxsq += x * x;

		y = atof(argv[1]);
		p->sumy += y;
		p->sumysq += y * y;

		p->sumxy += x * y;
	}
}
SQEXT_FUNC	sqlitex_sigma_final(sqlite3_context * context)
{
	ParStats *	p = sqlite3_aggregate_context(context, sizeof(ParStats));
	if (p->n >= 2)
		sqlite3_set_result_double(context, sqrt(psDispersionY(p) / ((double)(p->n) * (p->n - 1))) );
	else
		sqlite3_set_result_error(context, "sigma requires at least 2 rows", -1);
}

SQEXT_FUNC	sqlitex_variance_final(sqlite3_context * context)
{
	ParStats *	p = sqlite3_aggregate_context(context, sizeof(ParStats));
	if (p->n >= 2)
		sqlite3_set_result_double(context, psDispersionY(p) / ((double)(p->n) * (p->n - 1)) );
	else
		sqlite3_set_result_error(context, "variance requires at least 2 rows", -1);
}
SQEXT_FUNC	sqlitex_dispersion_final(sqlite3_context * context)
{
	ParStats *	p = sqlite3_aggregate_context(context, sizeof(ParStats));
	if (p->n >= 1)
		sqlite3_set_result_double(context, psDispersionY(p));
	else
		sqlite3_set_result_error(context, "dispersion requires at least 1 row", -1);
}
static double	psSlope(ParStats *	p)
{
	double	dx;
	if ((dx = psDispersionX(p)) == 0)
		return 0.;
	else
		return psDispersionXY(p) / dx;
}

SQEXT_FUNC	sqlitex_slope_final(sqlite3_context * context)
{
	ParStats *	p = sqlite3_aggregate_context(context, sizeof(ParStats));
	if (p->n >= 2)
			sqlite3_set_result_double(context, psSlope(p));
	else
		sqlite3_set_result_error(context, "slope requires at least 2 rows", -1);
}
SQEXT_FUNC	sqlitex_intercept_final(sqlite3_context * context)
{
	ParStats *	p = sqlite3_aggregate_context(context, sizeof(ParStats));
	if (p->n >= 2)
		sqlite3_set_result_double(context, (p->sumy - (psSlope(p) * p->sumx)) / p->n);
	else
		sqlite3_set_result_error(context, "intercept requires at least 2 rows", -1);
}
SQEXT_FUNC	sqlitex_corrcoeff_final(sqlite3_context * context)
{
	double	d;
	ParStats *	p = sqlite3_aggregate_context(context, sizeof(ParStats));
	if (p->n >= 2)
	{
		d = psDispersionX(p) * psDispersionY(p);
		if (d <= 0)
			sqlite3_set_result_double(context, 1.);
		else
			sqlite3_set_result_double(context, psDispersionXY(p) / sqrt(d));
	}
	else
	{
		sqlite3_set_result_error(context, "corrcoeff requires at least 2 rows", -1);
	}
}
SQEXT_FUNC	sqlitex_rand(sqlite3_context * context,int argc,const char** argv)
{
	int	n;
	if (argc < 1 || argv[0] == NULL || (n = atoi(argv[0])) == 0)
	{
		sqlite3_set_result_int(context, rand());
	}
	else
	{
		sqlite3_set_result_int(context, rand() % n);
	}
}
SQEXT_FUNC	sqlitex_srand(sqlite3_context * context,int argc,const char** argv)
{
	int	n;
	if (argc < 1 || argv[0] == NULL || (n = atoi(argv[0])) == 0)
	{
		n = time(NULL);
		srand((unsigned)n);
		sqlite3_set_result_int(context, n);
	}
	else
	{
		n = atoi(argv[0]);
		srand((unsigned)n);
		sqlite3_set_result_int(context, n);
	}
}

int		sqlitex_registerFunctions(sqlite3 * dbh)
{
   void (*xFunc)(sqlite3_context*,int,sqlite3_value **);
	static struct {char * name; int nArg; sqlFuncPtr f;} functions[] =
	{
		{"now", 0, sqlitex_now},
		{"format_gmtime", 2, sqlitex_formatGMTime},
		{"format_localtime", 2, sqlitex_formatLocalTime},
		{"age", 1, sqlitex_age},
		{"difftime", 2, sqlitex_difftime},
		{"distance", 4, sqlitex_distance},
		{"rand", 1, sqlitex_rand},
		{"srand", 1, sqlitex_srand},
		{NULL}
	};
	static struct {char * name; int nArg; sqlFuncPtr step; sqlFinalizePtr fin;} aggregates[] =
	{
		{"sigma", 1, sqlitex_collect1Stat, sqlitex_sigma_final},
		{"variance", 1, sqlitex_collect1Stat, sqlitex_variance_final},
		{"dispersion", 1, sqlitex_collect1Stat, sqlitex_dispersion_final},
		{"slope", 2, sqlitex_collect2Stats, sqlitex_slope_final},
		{"intercept", 2, sqlitex_collect2Stats, sqlitex_intercept_final},
		{"corrcoeff", 2, sqlitex_collect2Stats, sqlitex_corrcoeff_final},
		{NULL}
	};

    
	int		i;

	for (i = 0; functions[i].name != NULL; i++)
	{
		  void *pArg = 0;
                 struct FuncDef *pFunc = sqlite3FindFunction(dbh, functions[i].name, 
          strlen(functions[i].name), functions[i].nArg, functions[i].eTextRep, 0);
      if (sqlite3_create_function(dbh, functions[i].name, functions[i].nArg, functions[i].eTextRep,pArg,functions[i].xFunct, 0,0) != SQLITE_OK)
		{
			fprintf(stderr, "Can't register %s\n", functions[i].name);
		}
	}
	for (i = 0; aggregates[i].name != NULL; i++)
	{
		if (sqlite3_create_aggregate(dbh,
				aggregates[i].name,
				aggregates[i].nArg,
				aggregates[i].step,
				aggregates[i].fin, NULL) != SQLITE_OK)
		{
			fprintf(stderr, "Can't register %s\n", functions[i].name);
		}
	}
	return SQLITE_OK;
}

