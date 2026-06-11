class Solution {
    public double findMaxAverage(int[] nums, int k) {
      int sum=0;
      int left=0;
      for (int i=0; i<k; i++){
        sum= sum+nums[i];
      } 
      int result=sum;

      for (int right=k; right<nums.length; right++){
        sum= sum-nums[left];
        left++;
        sum=sum+nums[right];
        result= Math.max(sum,result);
      } 
      return (double) result/k;
    }
}