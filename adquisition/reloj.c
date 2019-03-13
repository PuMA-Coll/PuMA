#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <math.h>
#include <sys/time.h>

void wait_full_sec(void);

struct timeval ontime;

int main(void)
{
    time_t     now,now1;
    struct tm *ts,*ts1;
    struct timespec tstart = {0,0};
    char       buf[80],buf1[80];
    
    struct timeval tv;
	double time_offset=0;
	double time_offset2=0.0;
	int min, sec, hour, TZ=-3;
	char buffer[26];
    
    struct tm* tm_info;

	printf("============================\n");
	system("echo 'LINUX DATE TIMESTAMP: '; date --rfc-3339=\'ns\'");
	printf("============================\n");

    /* Obtener la hora actual en segundos*/
    now = time(NULL);
    ts = localtime(&now);
    strftime(buf, sizeof(buf), "%a %Y-%m-%d %H:%M:%S", ts);
    printf("localtime: %s <<< NORMALLY SHOULD BE OK!!!\n", buf);
    
    /* Obtener la hora actual en microsegundos*/
    gettimeofday(&tv, NULL);
    ts1 = localtime(&tv.tv_sec);
    strftime(buf1, sizeof(buf1), "%a %Y-%m-%d %H:%M:%S", ts1);
	printf("timeofday: %s.%06ld\n",buf1,tv.tv_usec);

//	printf("============================\n");	
//	system("echo 'LINUX DATE TIMESTAMP: '; date --rfc-3339=\'ns\'");

	printf("============================\n");
    
    
	gettimeofday(&ontime, NULL);
	tm_info = localtime(&ontime.tv_sec);
	strftime(buffer, 26, "%Y:%m:%d %H:%M:%S", tm_info);
	printf("Gettimeofday Input time   : %s.%06ld\n", buffer, tv.tv_usec);
    
    wait_full_sec();


	tm_info = localtime(&ontime.tv_sec);
	strftime(buffer, 26, "%Y:%m:%d %H:%M:%S", tm_info);

	printf("Gettimeofday Release time : %s.%06ld\n", buffer, ontime.tv_usec);

    printf("============================\n");    
    
 	/* Obtener la hora actual en microsegundos*/
    gettimeofday(&tv, NULL);
    ts = localtime(&tv.tv_sec);
    strftime(buf, sizeof(buf), "%a %Y-%m-%d %H:%M:%S", ts);
	printf("timeofday: %s.%06ld\n",buf,tv.tv_usec);
    
    /* Obtener la hora actual en segundos*/
    now1 = time(NULL);
    ts1 = localtime(&now1);
    strftime(buf1, sizeof(buf1), "%a %Y-%m-%d %H:%M:%S", ts1);
    printf("localtime: %s  <<< ALWAYS RETARDED ONE SECOND!!!\n", buf1);


    
    printf("============================\n");
    system("echo 'LINUX DATE TIMESTAMP: '; date --rfc-3339=\'ns\'");
    printf("============================\n");


	int r = clock_gettime(CLOCK_REALTIME, &tstart);
    ts1 = localtime(&tstart.tv_sec);
    strftime(buf1, sizeof(buf1), "%a %Y-%m-%d %H:%M:%S", ts1);
    printf("localtime: %s <<< MAY STILL BE RETARDED!!!\n", buf1);
    printf("nanoseconds: %ld \n",tstart.tv_nsec);


//	printf("============================\n");
//	system("echo 'LINUX DATE TIMESTAMP: '; date --rfc-3339=\'ns\'");
//	printf("============================\n");

	min=tm_info->tm_min;
	sec= tm_info->tm_sec ;
	hour=(tm_info->tm_hour)-TZ;

	time_offset=0;
	time_offset+=(double)((hour*60+min)*60+sec)/(24*60*60);

	time_offset2=(double)(hour*60+min)*60+sec;
	time_offset2=time_offset2*1.15740740740740744030e-5;

	printf("Day fraction 1 : %.20f day\n",time_offset);
	printf("Day fraction 2 : %.20f day\n",time_offset2);
	printf("Delta fraction : %.20f days\n",(time_offset2-time_offset));

	printf("Day seconds 1 : %.20f s\n",time_offset*86400.);
	printf("Day seconds 2 : %.20f s\n",time_offset2*86400.);
	printf("Difference    : %.20f ns\n",(time_offset2*86400.-time_offset*86400.)*1e9);

	printf("============================\n");

	/* Obtener la hora actual en segundos*/    
    now1 = time(NULL);
    ts1 = localtime(&now1);
    strftime(buf1, sizeof(buf1), "%a %Y-%m-%d %H:%M:%S", ts1);
    printf("localtime: %s <<< MAY STILL BE RETARDED!!!\n", buf1);


    return 0;
}


void wait_full_sec(void) {

	do{
		gettimeofday(&ontime, NULL);
   	}while(ontime.tv_usec!=0);

}
