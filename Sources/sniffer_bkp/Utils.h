#ifndef _UTILS__H_
#define _UTILS__H_ 1

#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>
#include <cstdio>    // For remove()
#include <fstream>   // For ifstream
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <queue>


class StringUtils
{
    public:

        //
        // String operations
        //

        const static std::string toLower(const char* str);

        const static void lTrim(std::string &s);

        const static void rTrim(std::string &s);

        const static void trim(std::string &s);

        const static std::string ltrimCopy(std::string s);

        const static std::string rtrimCopy(std::string s);

        const static std::string trimCopy(std::string s);

    private:

};

class OSUtils
{
    public:

        const static bool fileExists(const char* fileName);

        const static bool deleteFileIfExists(const char* filename);

    private:

};

/**
// Thread-safe queue
template <typename T>
class TSQueue 
{

	public:

        // Pushes an element to the queue
        void push(T item)
        {
            try
            {
                printf("-- push:lock(m_mutex)\n");
                // Acquire lock
                std::unique_lock<std::mutex> lock(m_mutex);

                // Add item
                m_queue.push(item);

                // Notify one thread that
                // is waiting
                //m_cond.notify_one();
            }
            catch(const std::exception& e)
            {
                printf("e.what:%s\n", e.what());
            }            
        }
    
        // Pops an element off the queue
        T pop()
        {
            try 
            {   
                // acquire lock
                printf("-- pop:lock(m_mutex)\n");
                std::unique_lock<std::mutex> lock(m_mutex);
        
                //// wait until queue is not empty
                //m_cond.wait(lock,
                //            [this]() { return !m_queue.empty(); });
        
                // retrieve item
                printf("-- retrieve item\n");
                if (m_queue.empty())
                {
                    printf("-- nullptr item\n");
                    return nullptr;
                }
                T item = m_queue.front();
                m_queue.pop();
        
                // return item
                return item;
            }
            catch(const std::exception e)
            {
                printf("e.what:%s\n", e.what());
            }
        }

	private:
		// Underlying queue
		std::queue<T> m_queue;
	  
		// mutex for thread synchronization
		std::mutex m_mutex;
	  
		// Condition variable for signaling
		//std::condition_variable m_cond;        
};
**/

template<typename T>
class TSQueue 
{
    public:
        void push(T const& value) 
        {
            // printf("push lock(m_mutex);\n");
            std::unique_lock<std::mutex> lock(m_mutex);
            // printf("m_queue.push(value);\n");
            m_queue.push(value);
            // printf("lock.unlock();\n");
            lock.unlock();
            // printf("m_cond.notify_one();\n");
            m_cond.notify_one();
        }

        bool empty() const 
        {
            // printf("\n");
            std::unique_lock<std::mutex> lock(m_mutex);
            // printf("\n");
            return m_queue.empty();
        }

        bool try_pop(T& popped_value) 
        {
            // printf("try_pop lock(m_mutex)\n");
            std::unique_lock<std::mutex> lock(m_mutex);
            if (m_queue.empty()) 
            {
                return false;
            }

            // printf("m_queue.front()\n");
            popped_value = m_queue.front();

            // printf("m_queue.pop();\n");
            m_queue.pop();

            return true;
        }

        void wait_and_pop(T& popped_value) 
        {
            std::unique_lock<std::mutex> lock(m_mutex);
            while (m_queue.empty()) 
            {
                m_cond.wait(lock);
            }

            popped_value = m_queue.front();
            m_queue.pop();
        }

    private:
        std::queue<T> m_queue;
        mutable std::mutex m_mutex;
        std::condition_variable m_cond;
};


#endif // _UTILS__H_

